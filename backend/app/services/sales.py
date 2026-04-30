from collections import defaultdict
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import BusinessError
from app.models.domain import (
    CashierShift,
    InventoryBatch,
    InventoryItem,
    LoyaltyLedger,
    Payment,
    PaymentMode,
    Product,
    Sale,
    SaleItem,
    SaleItemBatchAllocation,
    SaleReturn,
    SaleReturnItem,
    SaleStatus,
    ShiftStatus,
    StockMovement,
    StockMovementType,
    User,
)
from app.schemas.sales import SaleCreate, SaleReturnCreate
from app.services.decimal_utils import money, qty, split_inclusive_tax
from app.services.numbering import make_number


def _load_sale(db: Session, sale_id: int) -> Sale:
    sale = db.scalar(
        select(Sale)
        .where(Sale.id == sale_id)
        .options(
            selectinload(Sale.items).selectinload(SaleItem.allocations),
            selectinload(Sale.payments),
            selectinload(Sale.customer),
            selectinload(Sale.cashier),
        )
    )
    if not sale:
        raise BusinessError("Sale not found", 404)
    return sale


def _require_open_cash_shift(db: Session, cashier_id: int, payments: list) -> CashierShift | None:
    needs_cash = any(payment.mode == PaymentMode.CASH for payment in payments)
    shift = db.scalar(
        select(CashierShift).where(CashierShift.cashier_id == cashier_id, CashierShift.status == ShiftStatus.OPEN)
    )
    if needs_cash and not shift:
        raise BusinessError("Cash payments require an open cashier shift")
    return shift


def _calculate_line(product: Product, quantity: Decimal, discount_amount: Decimal) -> dict[str, Decimal]:
    quantity = qty(quantity)
    gross = money(product.selling_price * quantity)
    discount = money(discount_amount)
    if discount > gross:
        raise BusinessError(f"Discount cannot exceed line total for {product.name}")
    line_total = money(gross - discount)
    taxable, tax = split_inclusive_tax(line_total, product.gst_rate)
    return {
        "gross": gross,
        "discount": discount,
        "line_total": line_total,
        "taxable": taxable,
        "tax": tax,
    }


def create_sale(db: Session, payload: SaleCreate, current_user: User) -> Sale:
    try:
        product_ids = [item.product_id for item in payload.items]
        products = {
            product.id: product
            for product in db.scalars(select(Product).where(Product.id.in_(product_ids), Product.is_active.is_(True)))
        }
        if len(products) != len(product_ids):
            raise BusinessError("One or more products are not available")

        shift = _require_open_cash_shift(db, current_user.id, payload.payments)
        calculated_items = []
        subtotal = Decimal("0.00")
        discount_total = Decimal("0.00")
        taxable_total = Decimal("0.00")
        tax_total = Decimal("0.00")
        grand_total = Decimal("0.00")

        for item in payload.items:
            product = products[item.product_id]
            inventory = db.scalar(select(InventoryItem).where(InventoryItem.product_id == product.id).with_for_update())
            if not inventory or inventory.on_hand < item.quantity:
                raise BusinessError(f"Insufficient stock for {product.name}")
            line = _calculate_line(product, item.quantity, item.discount_amount)
            subtotal += line["gross"]
            discount_total += line["discount"]
            taxable_total += line["taxable"]
            tax_total += line["tax"]
            grand_total += line["line_total"]
            calculated_items.append((item, product, inventory, line))

        subtotal = money(subtotal)
        discount_total = money(discount_total)
        taxable_total = money(taxable_total)
        tax_total = money(tax_total)
        grand_total = money(grand_total)
        paid_total = money(sum((payment.amount for payment in payload.payments), Decimal("0.00")))
        if paid_total < grand_total:
            raise BusinessError("Paid amount is less than sale total")

        sale = Sale(
            invoice_number=make_number("INV"),
            cashier_id=current_user.id,
            customer_id=payload.customer_id,
            shift_id=shift.id if shift else None,
            subtotal=subtotal,
            discount_total=discount_total,
            taxable_total=taxable_total,
            tax_total=tax_total,
            grand_total=grand_total,
            paid_total=paid_total,
            change_due=money(paid_total - grand_total),
            notes=payload.notes,
        )
        db.add(sale)
        db.flush()

        for item, product, inventory, line in calculated_items:
            sale_item = SaleItem(
                sale_id=sale.id,
                product_id=product.id,
                product_name=product.name,
                sku=product.sku,
                barcode=product.barcode,
                quantity=qty(item.quantity),
                unit_price=product.selling_price,
                discount_amount=line["discount"],
                gst_rate=product.gst_rate,
                taxable_amount=line["taxable"],
                tax_amount=line["tax"],
                line_total=line["line_total"],
            )
            db.add(sale_item)
            db.flush()

            remaining = qty(item.quantity)
            inventory_before = inventory.on_hand
            inventory.on_hand = qty(inventory.on_hand - remaining)
            batches = list(
                db.scalars(
                    select(InventoryBatch)
                    .where(InventoryBatch.product_id == product.id, InventoryBatch.quantity_on_hand > 0)
                    .order_by(InventoryBatch.expiry_date.is_(None), InventoryBatch.expiry_date, InventoryBatch.created_at)
                    .with_for_update()
                )
            )
            for batch in batches:
                if remaining <= 0:
                    break
                take = qty(min(batch.quantity_on_hand, remaining))
                batch_before = batch.quantity_on_hand
                batch.quantity_on_hand = qty(batch.quantity_on_hand - take)
                remaining = qty(remaining - take)
                db.add(
                    SaleItemBatchAllocation(
                        sale_item_id=sale_item.id,
                        batch_id=batch.id,
                        batch_number=batch.batch_number,
                        expiry_date=batch.expiry_date,
                        quantity=take,
                    )
                )
                db.add(
                    StockMovement(
                        product_id=product.id,
                        batch_id=batch.id,
                        movement_type=StockMovementType.SALE_OUT,
                        quantity=take,
                        before_quantity=batch_before,
                        after_quantity=batch.quantity_on_hand,
                        reference_type="SALE",
                        reference_id=sale.id,
                        notes=f"Invoice {sale.invoice_number}",
                        created_by_id=current_user.id,
                    )
                )
            if remaining > 0:
                raise BusinessError(f"Insufficient batch stock for {product.name}")
            if inventory.on_hand < 0:
                raise BusinessError(f"Stock cannot go negative for {product.name}")
            if inventory_before - item.quantity != inventory.on_hand:
                raise BusinessError(f"Inventory reconciliation failed for {product.name}")

        for payment in payload.payments:
            db.add(Payment(sale_id=sale.id, mode=payment.mode, amount=money(payment.amount), reference=payment.reference))

        if payload.customer_id:
            points = int(grand_total // Decimal("100"))
            if points:
                db.add(
                    LoyaltyLedger(
                        customer_id=payload.customer_id,
                        sale_id=sale.id,
                        points=points,
                        description=f"Earned on invoice {sale.invoice_number}",
                    )
                )
        db.commit()
        return _load_sale(db, sale.id)
    except Exception:
        db.rollback()
        raise


def create_return(db: Session, sale_id: int, payload: SaleReturnCreate, current_user: User) -> SaleReturn:
    try:
        sale = _load_sale(db, sale_id)
        if sale.status == SaleStatus.VOID:
            raise BusinessError("Cannot return a void sale")
        sale_items_by_id = {item.id: item for item in sale.items}
        requested_by_item = defaultdict(Decimal)
        for item in payload.items:
            if item.sale_item_id not in sale_items_by_id:
                raise BusinessError("Return item does not belong to sale")
            requested_by_item[item.sale_item_id] += qty(item.quantity)

        refund_total = Decimal("0.00")
        return_record = SaleReturn(
            sale_id=sale.id,
            refund_mode=payload.refund_mode,
            refund_amount=Decimal("0.00"),
            reason=payload.reason,
            processed_by_id=current_user.id,
        )
        db.add(return_record)
        db.flush()

        for sale_item_id, return_qty in requested_by_item.items():
            sale_item = sale_items_by_id[sale_item_id]
            available = qty(sale_item.quantity - sale_item.returned_quantity)
            if return_qty > available:
                raise BusinessError(f"Return quantity exceeds sold quantity for {sale_item.product_name}")

            line_refund = money(sale_item.line_total * return_qty / sale_item.quantity)
            refund_total += line_refund
            sale_item.returned_quantity = qty(sale_item.returned_quantity + return_qty)
            remaining = return_qty

            inventory = db.scalar(select(InventoryItem).where(InventoryItem.product_id == sale_item.product_id).with_for_update())
            if not inventory:
                inventory = InventoryItem(product_id=sale_item.product_id, on_hand=Decimal("0.000"))
                db.add(inventory)
                db.flush()
            inventory.on_hand = qty(inventory.on_hand + return_qty)

            for allocation in sale_item.allocations:
                if remaining <= 0:
                    break
                alloc_available = qty(allocation.quantity - allocation.returned_quantity)
                if alloc_available <= 0:
                    continue
                restore = qty(min(alloc_available, remaining))
                allocation.returned_quantity = qty(allocation.returned_quantity + restore)
                remaining = qty(remaining - restore)
                if not allocation.batch_id:
                    raise BusinessError("Cannot restock return without original batch")
                batch = db.scalar(select(InventoryBatch).where(InventoryBatch.id == allocation.batch_id).with_for_update())
                if not batch:
                    raise BusinessError("Original stock batch no longer exists")
                batch_before = batch.quantity_on_hand
                batch.quantity_on_hand = qty(batch.quantity_on_hand + restore)
                db.add(
                    StockMovement(
                        product_id=sale_item.product_id,
                        batch_id=batch.id,
                        movement_type=StockMovementType.RETURN_IN,
                        quantity=restore,
                        before_quantity=batch_before,
                        after_quantity=batch.quantity_on_hand,
                        reference_type="SALE_RETURN",
                        reference_id=return_record.id,
                        notes=f"Return for invoice {sale.invoice_number}",
                        created_by_id=current_user.id,
                    )
                )
            if remaining > 0:
                raise BusinessError("Unable to allocate returned quantity to original batches")
            db.add(
                SaleReturnItem(
                    sale_return_id=return_record.id,
                    sale_item_id=sale_item.id,
                    product_id=sale_item.product_id,
                    quantity=return_qty,
                    refund_amount=line_refund,
                )
            )

        return_record.refund_amount = money(refund_total)
        all_returned = all(item.returned_quantity >= item.quantity for item in sale.items)
        any_returned = any(item.returned_quantity > 0 for item in sale.items)
        sale.status = SaleStatus.RETURNED if all_returned else SaleStatus.PARTIALLY_RETURNED if any_returned else SaleStatus.COMPLETED
        db.commit()
        db.refresh(return_record)
        return return_record
    except Exception:
        db.rollback()
        raise


def get_sale(db: Session, sale_id: int) -> Sale:
    return _load_sale(db, sale_id)
