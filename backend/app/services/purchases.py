from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.errors import BusinessError
from app.models.domain import (
    GoodsReceipt,
    GoodsReceiptItem,
    InventoryBatch,
    InventoryItem,
    Product,
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
    StockMovement,
    StockMovementType,
    Supplier,
    User,
)
from app.schemas.purchases import GoodsReceiptCreate, PurchaseOrderCreate
from app.services.decimal_utils import money, qty
from app.services.numbering import make_number


def _load_po(db: Session, po_id: int) -> PurchaseOrder:
    po = db.scalar(
        select(PurchaseOrder)
        .where(PurchaseOrder.id == po_id)
        .options(selectinload(PurchaseOrder.items), selectinload(PurchaseOrder.supplier), selectinload(PurchaseOrder.receipts))
    )
    if not po:
        raise BusinessError("Purchase order not found", 404)
    return po


def create_purchase_order(db: Session, payload: PurchaseOrderCreate, current_user: User) -> PurchaseOrder:
    try:
        supplier = db.get(Supplier, payload.supplier_id)
        if not supplier or not supplier.is_active:
            raise BusinessError("Supplier not found", 404)
        product_ids = [item.product_id for item in payload.items]
        products = {product.id: product for product in db.scalars(select(Product).where(Product.id.in_(product_ids)))}
        if len(products) != len(product_ids):
            raise BusinessError("One or more products were not found")

        subtotal = Decimal("0.00")
        tax_total = Decimal("0.00")
        po = PurchaseOrder(
            po_number=make_number("PO"),
            supplier_id=payload.supplier_id,
            expected_date=payload.expected_date,
            subtotal=Decimal("0.00"),
            tax_total=Decimal("0.00"),
            grand_total=Decimal("0.00"),
            notes=payload.notes,
            created_by_id=current_user.id,
        )
        db.add(po)
        db.flush()
        for item in payload.items:
            line_base = money(item.quantity_ordered * item.unit_cost)
            line_tax = money(line_base * item.gst_rate / Decimal("100"))
            line_total = money(line_base + line_tax)
            subtotal += line_base
            tax_total += line_tax
            db.add(
                PurchaseOrderItem(
                    purchase_order_id=po.id,
                    product_id=item.product_id,
                    quantity_ordered=qty(item.quantity_ordered),
                    unit_cost=money(item.unit_cost),
                    gst_rate=item.gst_rate,
                    line_total=line_total,
                )
            )
        po.subtotal = money(subtotal)
        po.tax_total = money(tax_total)
        po.grand_total = money(subtotal + tax_total)
        db.commit()
        return _load_po(db, po.id)
    except Exception:
        db.rollback()
        raise


def receive_goods(db: Session, po_id: int, payload: GoodsReceiptCreate, current_user: User) -> GoodsReceipt:
    try:
        po = _load_po(db, po_id)
        if po.status in {PurchaseOrderStatus.CANCELLED, PurchaseOrderStatus.RECEIVED}:
            raise BusinessError("Purchase order cannot receive more goods")
        po_items = {item.id: item for item in po.items}

        grn = GoodsReceipt(
            grn_number=make_number("GRN"),
            purchase_order_id=po.id,
            supplier_invoice_number=payload.supplier_invoice_number,
            notes=payload.notes,
            received_by_id=current_user.id,
        )
        db.add(grn)
        db.flush()

        for item in payload.items:
            po_item = po_items.get(item.purchase_order_item_id)
            if not po_item:
                raise BusinessError("Receipt item does not belong to purchase order")
            remaining = qty(po_item.quantity_ordered - po_item.quantity_received)
            incoming = qty(item.quantity_received)
            if incoming > remaining:
                raise BusinessError("Received quantity exceeds remaining purchase order quantity")

            product = db.get(Product, po_item.product_id)
            if not product:
                raise BusinessError("Product not found", 404)
            inventory = db.scalar(select(InventoryItem).where(InventoryItem.product_id == product.id).with_for_update())
            if not inventory:
                inventory = InventoryItem(product_id=product.id, on_hand=Decimal("0.000"), reorder_level=Decimal("5.000"))
                db.add(inventory)
                db.flush()
            before_inventory = inventory.on_hand
            inventory.on_hand = qty(inventory.on_hand + incoming)

            batch = db.scalar(
                select(InventoryBatch)
                .where(InventoryBatch.product_id == product.id, InventoryBatch.batch_number == item.batch_number)
                .with_for_update()
            )
            if not batch:
                batch = InventoryBatch(
                    product_id=product.id,
                    batch_number=item.batch_number,
                    expiry_date=item.expiry_date,
                    cost_price=money(item.unit_cost),
                    received_quantity=Decimal("0.000"),
                    quantity_on_hand=Decimal("0.000"),
                )
                db.add(batch)
                db.flush()
            batch_before = batch.quantity_on_hand
            batch.received_quantity = qty(batch.received_quantity + incoming)
            batch.quantity_on_hand = qty(batch.quantity_on_hand + incoming)
            batch.cost_price = money(item.unit_cost)
            if item.expiry_date:
                batch.expiry_date = item.expiry_date
            po_item.quantity_received = qty(po_item.quantity_received + incoming)

            db.add(
                GoodsReceiptItem(
                    goods_receipt_id=grn.id,
                    purchase_order_item_id=po_item.id,
                    product_id=product.id,
                    batch_id=batch.id,
                    batch_number=batch.batch_number,
                    expiry_date=batch.expiry_date,
                    quantity_received=incoming,
                    unit_cost=money(item.unit_cost),
                )
            )
            db.add(
                StockMovement(
                    product_id=product.id,
                    batch_id=batch.id,
                    movement_type=StockMovementType.PURCHASE_IN,
                    quantity=incoming,
                    before_quantity=batch_before,
                    after_quantity=batch.quantity_on_hand,
                    reference_type="GRN",
                    reference_id=grn.id,
                    notes=f"GRN {grn.grn_number}",
                    created_by_id=current_user.id,
                )
            )
            if before_inventory + incoming != inventory.on_hand:
                raise BusinessError("Inventory reconciliation failed during receipt")

        if all(item.quantity_received >= item.quantity_ordered for item in po.items):
            po.status = PurchaseOrderStatus.RECEIVED
        else:
            po.status = PurchaseOrderStatus.PARTIAL
        db.commit()
        db.refresh(grn)
        return grn
    except Exception:
        db.rollback()
        raise


def get_purchase_order(db: Session, po_id: int) -> PurchaseOrder:
    return _load_po(db, po_id)
