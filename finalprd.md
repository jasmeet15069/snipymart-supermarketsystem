# SnipyMart Supermarket ERP + POS - Detailed Final PRD

## 1. Document Control

### Document Purpose

This document is the detailed final product requirements document for the SnipyMart Supermarket ERP + POS project.

It describes the final approved product scope, implemented business workflows, technical architecture, data model, deployment model, user roles, acceptance criteria, and maintenance boundaries.

### Scope Status

The product scope is closed.

No additional feature modules are planned after this document. Any later work must be limited to necessary fixes or explicitly approved scope amendments.

Allowed post-final work:

- Bug fixes.
- Security fixes.
- Deployment stability fixes.
- Database/data integrity fixes.
- Compatibility fixes required by hosting, database, browser, or framework changes.
- Documentation corrections.
- Minor UI clarity fixes that do not add new business workflows.

Not allowed without explicit re-approval:

- New modules.
- New major workflows.
- Multi-store expansion.
- Mobile app expansion.
- Offline POS expansion.
- Accounting expansion.
- Hardware workflow expansion beyond current browser/manual/USB scanner support.

### Product Version

Final approved scope: V1.2 Closed Scope

### Project Location

`C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem`

### Repository

`https://github.com/jasmeet15069/snipymart-supermarketsystem`

### Production URLs

- Vercel application: `https://snipymart-supermarketsystem.vercel.app`
- VPS frontend: `http://45.79.124.28:3001`
- VPS backend health: `http://45.79.124.28:8010/health`
- VPS backend API: `http://45.79.124.28:8010/api/v1`

## 2. Executive Summary

SnipyMart is a single-store supermarket ERP + POS application for supermarket owners, cashiers, and inventory/purchase staff.

The system supports the complete approved operating workflow for a single supermarket:

- Product catalog management.
- Barcode-based product lookup.
- Inventory and stock visibility.
- Batch and expiry tracking fields.
- POS cart and billing.
- GST/tax and discount calculation.
- Cash, UPI, and card payments.
- Sale persistence.
- Invoice/receipt workflow.
- Sales returns.
- Supplier management.
- Purchase orders.
- Goods received notes.
- Customer management.
- Loyalty ledger.
- Cashier shifts.
- Admin/Cashier access control.
- Dashboard and reports.
- Deployed backend/frontend on Vercel and VPS.
- Aiven MySQL database.

The product is intended to be practical daily-use supermarket software, not a prototype-only CRUD application.

## 3. Product Vision

SnipyMart should help a supermarket run core daily operations from a browser-based system.

The cashier must be able to bill quickly. The owner/admin must be able to see business health and maintain master data. Inventory and purchase staff must be able to receive goods and keep stock accurate.

The final approved product is limited to a single-store supermarket ERP + POS. This PRD does not include a roadmap for new features.

## 4. Business Objectives

### Primary Objectives

- Reduce manual billing effort.
- Improve product lookup speed through barcode/manual search.
- Keep product, stock, sales, purchases, customers, and users in one system.
- Reduce inventory errors.
- Prevent negative stock.
- Maintain transaction history.
- Provide basic owner visibility into sales and stock.
- Support GST-inclusive pricing and tax tracking.

### Success Criteria

- Admin can manage business data.
- Cashier can complete POS billing.
- Products can be searched by barcode.
- Stock reduces after sale.
- Stock increases after goods receipt.
- Sales and purchase records are persisted.
- Reports load from stored transactions.
- User roles restrict access.
- Deployed application remains reachable on Vercel and VPS.

## 5. User Personas

## 5.1 Admin / Store Owner

### Responsibilities

- Manage products and pricing.
- Maintain suppliers.
- Create and track purchase orders.
- Review sales and reports.
- Manage users.
- Review inventory and low stock.
- View customer data.

### Needs

- Complete control of master data.
- Accurate inventory and transaction records.
- Clear reporting.
- Secure user access.
- Simple screens for routine updates.

### Access Level

Admin has full application access.

## 5.2 Cashier

### Responsibilities

- Open/current shift usage.
- Search or scan products.
- Add products to cart.
- Adjust quantity and discounts.
- Collect payment.
- Complete sale.
- Generate receipt/invoice.
- Handle allowed returns.

### Needs

- Fast POS screen.
- Minimal navigation.
- Clear totals and payment status.
- Barcode input support.
- Reliable stock validation.

### Access Level

Cashier has POS-focused access.

## 5.3 Inventory/Purchase Staff

### Responsibilities

- Track stock.
- Receive goods.
- Review batches/expiry.
- Review purchase orders.
- Confirm stock movements.

### Needs

- Inventory list.
- Batch and expiry visibility.
- Purchase order and GRN workflow.
- Stock movement traceability.

### Access Level

Handled through Admin-level workflow in the current closed scope.

## 6. Final Scope

## 6.1 In Scope

The following product capabilities are final and approved:

- Single-store operation.
- Admin and Cashier users.
- JWT authentication.
- Product catalog.
- Product categories.
- Barcode storage and lookup.
- Inventory items.
- Inventory batches.
- Expiry and batch fields.
- Stock movement history.
- POS cart.
- POS checkout.
- GST/tax calculations.
- Discounts.
- Cash, UPI, and card payments.
- Invoice/receipt view.
- Sales records.
- Basic sale returns.
- Suppliers.
- Purchase orders.
- Goods received notes.
- Customer records.
- Loyalty ledger.
- Cashier shifts.
- Dashboard KPIs.
- Revenue/top-product reports.
- User management.
- Seed data.
- Vercel deployment.
- VPS Docker deployment.

## 6.2 Out of Scope Unless Re-Approved

The following are excluded from the final approved product scope:

- Multi-store or multi-branch inventory.
- Store transfers.
- Offline POS sync.
- Mobile app.
- Native desktop app.
- Full accounting ledger.
- GST filing automation.
- Advanced promotions/coupons engine.
- Vendor payment reconciliation.
- Hardware receipt-printer driver integration beyond browser print support.
- Barcode label generation/printing.
- Automated forecasting.
- Warehouse management.
- Advanced permission matrix beyond Admin/Cashier.

## 7. Technology Stack

## 7.1 Backend

- Python.
- FastAPI.
- SQLAlchemy.
- Alembic.
- Pydantic.
- PyMySQL.
- JWT authentication.
- Aiven MySQL.

## 7.2 Frontend

- Next.js App Router.
- TypeScript.
- Tailwind CSS.
- Axios.
- TanStack Query.
- Lucide icons.
- Sonner toasts.

## 7.3 Deployment

- Vercel Services for web deployment.
- Docker and Docker Compose.
- VPS deployment with Docker containers.
- Aiven MySQL for primary database.

## 8. Repository Structure

The repository is organized as:

```text
erpsystem/
  backend/
    alembic/
    app/
      core/
      models/
      routes/
      schemas/
      services/
      seed.py
    requirements.txt
    Dockerfile
  frontend/
    src/
      app/
      components/
      lib/
    package.json
    Dockerfile
  docs/
    barcode-sources.md
  PRD.md
  FINAL_PRD.md
  finalprd.md
  README.md
  docker-compose.yml
  docker-compose.prod.yml
  vercel.json
```

## 9. Backend Architecture

## 9.1 Core Layers

### Core

Handles configuration, database connection, auth dependencies, logging, errors, and CORS.

### Models

Defines normalized SQLAlchemy domain models.

### Schemas

Defines Pydantic request and response contracts.

### Routes

Defines HTTP endpoints under `/api/v1`.

### Services

Contains business logic and transactional workflows.

### Alembic

Manages schema migrations.

### Seed

Loads realistic business seed data.

## 9.2 Backend Design Principles

- Keep HTTP handlers thin.
- Keep business logic in service functions.
- Keep schema validation explicit.
- Keep database changes in Alembic migrations.
- Keep secrets in environment variables only.
- Keep stock-changing operations transactional.

## 10. Frontend Architecture

## 10.1 App Router Pages

Implemented frontend pages:

- `/login`
- `/dashboard`
- `/pos`
- `/products`
- `/inventory`
- `/sales`
- `/reports`
- `/suppliers`
- `/purchases`
- `/customers`
- `/settings/users`

## 10.2 Frontend Design Principles

- POS should be the fastest workflow.
- Tables should show useful business data.
- Forms should stay simple and predictable.
- Toasts should communicate success/failure.
- API client should be centralized.
- Auth state should be shared through providers.
- UI should be practical and work-focused.

## 11. Data Model

## 11.1 User and Access

### User

Stores employee login and role data.

Key fields:

- Email.
- Full name.
- Hashed password.
- Role.
- Active status.

Roles:

- Admin.
- Cashier.

## 11.2 Catalog

### Category

Stores product grouping and default GST rate.

### Product

Stores product master data.

Key fields:

- Name.
- SKU.
- Barcode.
- Brand.
- HSN code.
- Category.
- Shelf location.
- Selling price.
- Cost price.
- GST rate.
- Unit.
- Active status.

## 11.3 Inventory

### InventoryItem

Stores product stock summary.

Key fields:

- Product.
- On-hand quantity.
- Reorder level.
- Safety stock.

### InventoryBatch

Stores batch-level inventory.

Key fields:

- Product.
- Batch number.
- Expiry date.
- Supplier batch code.
- MRP.
- Quantity available.

### StockMovement

Stores every stock-changing event.

Movement sources include:

- Opening stock.
- Sale.
- Return.
- Goods receipt.
- Adjustment.

## 11.4 POS and Sales

### Sale

Stores sale header.

Key fields:

- Invoice number.
- Customer.
- Cashier.
- Channel.
- Payment status.
- Subtotal.
- Discount.
- Tax.
- Total.
- Notes.

### SaleItem

Stores immutable product sale snapshots.

Key fields:

- Product.
- SKU snapshot.
- Product name snapshot.
- Quantity.
- Unit price.
- GST rate.
- Taxable value.
- Tax amount.
- Discount amount.
- Line total.

### Payment

Stores sale payments.

Payment modes:

- Cash.
- UPI.
- Card.

### SaleReturn

Stores return transaction header.

### SaleReturnItem

Stores returned sale line quantities and amounts.

## 11.5 Purchases

### Supplier

Stores vendor records.

Key fields:

- Name.
- Contact person.
- Phone.
- Email.
- Address.
- GSTIN.
- Payment terms.
- Credit days.

### PurchaseOrder

Stores purchase order header.

### PurchaseOrderItem

Stores ordered product quantities and costs.

### GoodsReceipt

Stores goods received note header.

### GoodsReceiptItem

Stores received product quantities and batch details.

## 11.6 Customers and Loyalty

### Customer

Stores customer profile.

Key fields:

- Name.
- Phone.
- Email.
- Address.
- Loyalty points.
- Loyalty tier.
- Credit limit.

### LoyaltyLedger

Stores earn/reversal entries linked to sales and returns.

## 11.7 Cash Control

### CashierShift

Stores cashier shift lifecycle.

Key fields:

- Cashier.
- Opening balance.
- Closing balance.
- Opened time.
- Closed time.
- Status.

## 12. Business Workflows

## 12.1 Login Workflow

1. User opens login page.
2. User enters email and password or uses demo Admin/Cashier button.
3. Frontend sends credentials to backend.
4. Backend validates password hash.
5. Backend returns access and refresh tokens.
6. Frontend stores tokens.
7. Frontend loads current user.
8. User is routed to allowed pages.

## 12.2 POS Sale Workflow

1. Cashier opens POS screen.
2. Cashier searches or scans product barcode.
3. System finds matching product.
4. Cashier adds product to cart.
5. Cashier adjusts quantity/discount if needed.
6. System validates stock.
7. System calculates subtotal, discount, GST, total, paid amount, balance, and change.
8. Cashier selects payment mode.
9. Backend creates sale transaction.
10. Backend creates sale items.
11. Backend creates payment records.
12. Backend deducts stock.
13. Backend creates stock movements.
14. Backend updates customer loyalty where applicable.
15. Frontend shows invoice/receipt result.

## 12.3 Purchase and GRN Workflow

1. Admin creates supplier if needed.
2. Admin creates purchase order.
3. Purchase order contains product line items.
4. Goods arrive.
5. Admin records goods receipt.
6. Backend creates/updates inventory batch.
7. Backend increases stock.
8. Backend creates stock movement.
9. Backend updates purchase order received status.

## 12.4 Return Workflow

1. Admin/Cashier selects sale.
2. User enters return quantities.
3. Backend validates returnable quantity.
4. Backend creates return record.
5. Backend restores stock.
6. Backend creates stock movement.
7. Backend adjusts loyalty ledger where applicable.

## 12.5 Inventory Monitoring Workflow

1. Admin opens inventory page.
2. System displays product stock.
3. Admin reviews reorder level and safety stock.
4. Low stock can be inferred from on-hand quantity against reorder level.
5. Stock movements allow traceability.

## 13. Barcode Requirements

## 13.1 Barcode Behavior

The system supports:

- Manual barcode entry.
- USB scanner input.
- Camera scanning where supported by browser and secure context.
- Product lookup by barcode in POS and product APIs.

## 13.2 Seeded Barcode Data

Seeded product barcodes include:

```text
690225103176  - India Gate Basmati Sella Rice 5kg
8901725121129 - Aashirvaad Shudh Chakki Atta 5kg
8904043901015 - Tata Salt 1kg
8906007280242 - Fortune Sunlite Refined Sunflower Oil 1L
8901262260121 - Amul Taaza Toned Milk 1L
8901262010023 - Amul Salted Butter 500g
8901063341500 - Britannia Bread 400g
8901491101837 - Lay's American Style Cream & Onion 52g
8901719113390 - Parle-G Gold Biscuits 250g
8901030681905 - Surf Excel Quick Wash Detergent Powder 1kg
8901030743467 - Vim Dishwash Bar 300g
8901314765314 - Colgate Strong Teeth Toothpaste 200g
6161100956780 - Dettol Original Soap 125g
8901764012273 - Coca-Cola Original Taste 750ml
8901052005185 - Tata Tea Premium 250g
4011          - Robusta Banana PLU
```

Barcode source notes are maintained in:

`docs/barcode-sources.md`

## 14. API Requirements

## 14.1 Authentication API

Required endpoints:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`

## 14.2 Product API

Required capabilities:

- List products.
- Create product.
- Update product.
- Search product by barcode/SKU/name.
- Return business fields needed by POS and tables.

## 14.3 Inventory API

Required capabilities:

- List inventory.
- Show stock quantities.
- Show batch/expiry metadata.
- Show stock movement history.

## 14.4 Sales API

Required capabilities:

- Create sale.
- List sales.
- Retrieve sale.
- Retrieve invoice data.
- Create return.

## 14.5 Purchase API

Required capabilities:

- Create purchase order.
- List purchase orders.
- Receive goods.
- Update stock on GRN.

## 14.6 Customer API

Required capabilities:

- List customers.
- Create customer.
- Update customer.
- Show customer history through sales.

## 14.7 Reports API

Required capabilities:

- Dashboard metrics.
- Revenue summary.
- Top products.
- Low-stock indicators.

## 15. Security Requirements

## 15.1 Authentication

- Passwords must be hashed.
- JWT access token must be required for protected APIs.
- Refresh token flow must support continued sessions.

## 15.2 Authorization

- Admin can access management modules.
- Cashier can access POS-related workflows.
- Unauthorized users must be blocked.

## 15.3 Secrets

- Database URL must not be committed.
- Secret key must not be committed.
- Vercel secrets must stay in Vercel env.
- Local secrets must stay in `.env`.

## 15.4 CORS

- Backend must allow approved frontend origins.
- Vercel frontend must reach Vercel backend service.
- Local frontend must reach local backend.

## 16. Deployment Requirements

## 16.1 Local

Backend:

```bash
cd backend
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

## 16.2 Vercel

Vercel uses `vercel.json` with services:

- Frontend service at `/`.
- Backend service at `/_/backend`.

Required Vercel production environment variables:

- `DATABASE_URL`
- `SECRET_KEY`
- `ENVIRONMENT`
- `BACKEND_CORS_ORIGINS`

## 16.3 VPS

VPS deployment uses Docker containers:

- `snipymart-v1-frontend`
- `snipymart-v1-backend`

Active ports:

- Frontend: `3001`
- Backend: `8010`

## 17. Data Integrity Requirements

- Product SKU should be unique.
- Barcode should identify a product for POS lookup.
- Sale items should preserve snapshots.
- Stock cannot become negative.
- Stock movement must be created for each stock change.
- GRN must increase stock.
- Sale must decrease stock.
- Return must restore stock.
- Return quantity cannot exceed sold quantity.
- Payment totals must reconcile with sale totals.
- Customer loyalty changes must be ledgered.

## 18. Acceptance Criteria

## 18.1 Authentication

- Admin login works.
- Cashier login works.
- Invalid credentials fail.
- Current user endpoint returns authenticated user.
- Protected routes require token.

## 18.2 POS

- POS page loads.
- Product barcode search works.
- Product can be added to cart.
- Quantity changes update totals.
- Payment mode can be selected.
- Sale can be completed when stock exists.
- Stock decreases after sale.

## 18.3 Inventory

- Inventory page loads.
- Product quantities are visible.
- Batch/expiry metadata is available where seeded.
- Stock movements exist.
- Negative stock is blocked.

## 18.4 Purchasing

- Suppliers load.
- Purchase orders load.
- GRN workflow exists.
- Received stock increases inventory.

## 18.5 Customers

- Customers load.
- Customer can be created/updated.
- Customer can be attached to sale.
- Loyalty records update through sale/return.

## 18.6 Reports

- Dashboard loads.
- Revenue data loads.
- Top products load.
- Reports are based on persisted transactions.

## 18.7 Deployment

- Vercel frontend loads.
- Vercel backend health returns `{"status":"ok"}`.
- Vercel login works.
- VPS frontend responds.
- VPS backend health responds.

## 19. Final Closed-Scope Checklist

- [x] Product scope is defined.
- [x] Feature roadmap is closed.
- [x] No future feature modules are planned.
- [x] Post-final work is restricted to maintenance and necessary fixes.
- [x] Admin role is final.
- [x] Cashier role is final.
- [x] Single-store scope is final.
- [x] POS workflow is final.
- [x] Product/inventory/purchase/customer/sales/report modules are final.
- [x] Barcode lookup behavior is final.
- [x] Vercel and VPS deployment support are accepted.

## 20. Risks and Constraints

- Camera scanner behavior depends on browser support and permissions.
- Barcode data can vary by product region and packaging.
- Fresh produce may use PLU or store-generated labels instead of EAN/UPC.
- Vercel serverless backend can have cold starts.
- Direct serverless database access requires careful connection handling at scale.
- Legacy backup table should not be dropped without explicit approval.
- Reporting is intentionally limited to the approved dashboard/reporting scope.

## 21. Final Product Decision

SnipyMart V1.2 Closed Scope is the final approved version of the supermarket ERP + POS project.

The project is considered feature-complete for the approved single-store ERP + POS scope.

No new features should be added unless they are necessary for bug resolution, security, deployment stability, data integrity, compliance, or required infrastructure compatibility.

Any request outside those boundaries must be handled as a formal scope amendment, not as continuation of this final PRD.
