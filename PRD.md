# SnipyMart Supermarket ERP + POS PRD

## Summary

SnipyMart is a production-oriented supermarket ERP + POS system built as a full-stack monorepo in:

`C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem`

Current release: **V1.2**

The system supports day-to-day supermarket workflows: cashier billing, inventory control, product catalog management, supplier purchasing, goods receipt, customers, users, roles, reports, barcode lookup, stock movements, and seeded business data.

## Current Deployment

- GitHub: `https://github.com/jasmeet15069/snipymart-supermarketsystem`
- Vercel frontend/backend services: `https://snipymart-supermarketsystem.vercel.app`
- VPS frontend: `http://45.79.124.28:3001`
- VPS backend health: `http://45.79.124.28:8010/health`
- VPS backend API: `http://45.79.124.28:8010/api/v1`
- Database: Aiven MySQL
- Secrets: stored in local `.env` and Vercel environment variables, not committed.

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- PyMySQL
- JWT authentication
- MySQL on Aiven

### Frontend

- Next.js App Router
- TypeScript
- Tailwind CSS
- Axios
- TanStack Query
- Lucide icons
- Sonner toasts

### Deployment

- Vercel Services configuration through `vercel.json`
- Dockerfiles for backend and frontend
- Docker Compose files for production/local orchestration
- VPS deployment using Docker containers

## What Is Built Till Now

### Backend Structure

The backend uses a modular FastAPI structure:

- `app/core`: config, database, auth dependencies, security, errors, logging.
- `app/models`: normalized SQLAlchemy domain models.
- `app/schemas`: Pydantic request/response schemas.
- `app/routes`: versioned API routers.
- `app/services`: transactional business logic.
- `alembic`: database migrations.
- `app/seed.py`: realistic business seed data.

### Backend Modules

Implemented modules:

- Authentication and JWT token flow.
- Admin/Cashier role support.
- Product and category management.
- Inventory tracking.
- Batch and expiry tracking fields.
- Stock movement logging.
- POS sale creation.
- Sales history.
- Invoice data.
- Supplier management.
- Purchase orders.
- Goods received / GRN.
- Customer management.
- Loyalty points ledger.
- Cashier shifts.
- Dashboard and reports.
- User management.
- Seed data.

### Core Models

Implemented database entities include:

- `User`
- `Category`
- `Product`
- `InventoryItem`
- `InventoryBatch`
- `StockMovement`
- `Sale`
- `SaleItem`
- `Payment`
- `SaleReturn`
- `SaleReturnItem`
- `Supplier`
- `PurchaseOrder`
- `PurchaseOrderItem`
- `GoodsReceipt`
- `GoodsReceiptItem`
- `Customer`
- `LoyaltyLedger`
- `CashierShift`

## Business Logic Implemented

### POS Sale Flow

The system supports:

- Product lookup by barcode, SKU, name, brand, HSN code, or shelf location.
- Cart creation.
- Stock validation before sale.
- GST/tax calculation.
- Discount calculation.
- Cash, UPI, and card payments.
- Sale persistence.
- Payment persistence.
- Inventory deduction.
- Stock movement creation.
- Customer loyalty update.
- Invoice/receipt data.

### Purchase Flow

The system supports:

- Supplier records.
- Purchase order creation.
- Purchase order items.
- Goods received notes.
- Batch creation/update on receipt.
- Stock increase on GRN.
- Stock movement creation.
- Purchase order received status updates.

### Inventory Logic

The system supports:

- On-hand stock tracking.
- Reorder levels.
- Safety stock fields.
- Inventory batches.
- Expiry dates.
- Supplier batch codes.
- MRP fields.
- Negative-stock prevention in service logic.
- Low-stock reporting support.

### Customer and Loyalty Logic

The system supports:

- Customer records.
- Customer purchase history through sales.
- Loyalty points.
- Loyalty tiers.
- Loyalty ledger entries.
- Point reversal on returns.

### Return Flow

The system supports:

- Sale return records.
- Return line items.
- Refund mode.
- Return quantity validation.
- Stock restoration.
- Loyalty adjustment.

## Frontend Pages

Implemented pages:

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

## Frontend UX

Implemented UI behavior:

- Fast POS billing screen.
- Barcode/manual search input.
- Camera barcode scanner support where browser permissions and HTTPS/local rules allow it.
- USB scanner support through keyboard-style barcode input.
- Product search and add-to-cart.
- Cart quantity controls.
- Discount/payment calculations.
- Payment mode selection.
- Invoice/receipt view support.
- Admin/Cashier quick login buttons.
- Tables for core modules.
- Forms for product/supplier/customer/user data.
- Loading states.
- Empty states.
- Error states.
- Toast notifications.
- Auth token refresh handling.
- Protected route behavior.

## Barcode Support

Barcode lookup is implemented through product barcode fields in the database.

Current seeded barcodes include verified public product barcode records where available:

```text
8901262260121 - Amul Taaza Toned Milk 1L
8901719113390 - Parle-G Gold Biscuits 250g
8901764012273 - Coca-Cola Original Taste 750ml
8904043901015 - Tata Salt 1kg
8901262010023 - Amul Salted Butter 500g
8901725121129 - Aashirvaad Shudh Chakki Atta 5kg
8906007280242 - Fortune Sunlite Refined Sunflower Oil 1L
8901030681905 - Surf Excel Quick Wash Detergent Powder 1kg
8901030743467 - Vim Dishwash Bar 300g
8901314765314 - Colgate Strong Teeth Toothpaste 200g
6161100956780 - Dettol Original Soap 125g
4011          - Robusta Banana PLU
```

Barcode source notes are documented in:

`docs/barcode-sources.md`

Fresh produce uses PLU-style codes. For bananas, `4011` is used as the produce PLU.

## API Surface

Implemented API groups include:

- `/api/v1/auth`
- `/api/v1/users`
- `/api/v1/categories`
- `/api/v1/products`
- `/api/v1/inventory`
- `/api/v1/sales`
- `/api/v1/shifts`
- `/api/v1/suppliers`
- `/api/v1/purchase-orders`
- `/api/v1/customers`
- `/api/v1/reports`

Representative flows:

- `POST /api/v1/auth/login`
- `POST /api/v1/auth/refresh`
- `GET /api/v1/auth/me`
- `GET /api/v1/products`
- `POST /api/v1/products`
- `GET /api/v1/inventory`
- `GET /api/v1/sales`
- `POST /api/v1/sales`
- `POST /api/v1/sales/{id}/returns`
- `POST /api/v1/shifts/open`
- `GET /api/v1/shifts/current`
- `POST /api/v1/shifts/{id}/close`
- `GET /api/v1/suppliers`
- `POST /api/v1/purchase-orders`
- `POST /api/v1/purchase-orders/{id}/receive`
- `GET /api/v1/customers`
- `GET /api/v1/reports/dashboard`

## Security

Implemented:

- JWT access tokens.
- JWT refresh tokens.
- Password hashing.
- Authenticated API routes.
- Admin and Cashier roles.
- CORS configuration.
- Vercel production environment variables.

Role expectations:

- Admin can manage catalog, inventory, suppliers, purchases, reports, users, and settings.
- Cashier can use POS, shifts, customers, sales, and allowed return workflows.

## Database and Migrations

Database:

- Primary database is Aiven MySQL.
- Local `.env` stores the Aiven connection string.
- Vercel production env stores required backend variables.
- Real secrets are ignored by Git.

Migrations:

- `0002_repair_legacy_sales_table`: repaired old flat sales table into normalized sales table.
- `0003_business_table_enhancements`: added business columns for supermarket workflows.
- `0004_drop_legacy_sales_flat`: prepared but not applied, because it permanently drops the old legacy backup table.

Important note:

The active normalized `sales` table is required for POS, reports, returns, inventory deduction, payments, and loyalty. The old `legacy_sales_flat` backup table should only be dropped after explicit approval.

## Seed Data

Seed data includes:

- Admin user.
- Cashier user.
- Additional users.
- Product categories.
- 16 realistic products.
- Verified barcode values.
- Inventory items.
- Inventory batches.
- Opening stock.
- Suppliers.
- Customers.
- Purchase orders.
- Goods received notes.
- POS sales.
- Sale returns.
- Stock movements.
- Loyalty records.

Default demo users:

```text
Admin:
admin@snipymart.in
Admin@12345

Cashier:
cashier@snipymart.in
Cashier@12345
```

## Setup Flow

### Backend

1. Copy `backend/.env.example` to `backend/.env`.
2. Add the Aiven MySQL connection string and secret key.
3. Create and activate a Python virtual environment.
4. Install dependencies:

```bash
python -m pip install -r backend/requirements.txt
```

5. Run migrations:

```bash
cd backend
python -m alembic upgrade head
```

6. Seed data:

```bash
python -m app.seed
```

7. Start backend:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

### Frontend

1. Copy `frontend/.env.local.example` to `frontend/.env.local`.
2. Install dependencies:

```bash
cd frontend
npm install
```

3. Start development server:

```bash
npm run dev
```

4. Production local start:

```bash
npm run build
npm run start
```

## Verification Done

Completed checks:

- Backend tests passed.
- Frontend typecheck passed.
- Frontend lint passed.
- Frontend production build passed.
- Local login works.
- Vercel login works.
- Vercel backend health works.
- Vercel barcode lookup works.
- Aiven seed script applied successfully.
- Product barcode search returns expected products.
- GitHub `main` is clean and pushed.

## Acceptance Status

Accepted for V1.2:

- Admin can log in.
- Cashier can log in.
- Products load.
- Inventory loads.
- Users load.
- POS loads.
- POS can search by barcode.
- Reports/dashboard APIs respond.
- Suppliers/customers/purchases modules respond.
- Seeded products include usable barcodes.
- Deployed Vercel backend is healthy.
- Deployed VPS containers are available.

## Remaining Gaps / Next Phase

Recommended next work:

- Add barcode label generation and printing.
- Add product CSV import/export.
- Add receipt PDF export.
- Add frontend automated tests.
- Add more backend tests for returns, shifts, and purchases.
- Add audit logging.
- Add multi-store/branch support.
- Add stock adjustment approval workflow.
- Add supplier payment tracking.
- Add customer loyalty redemption UI.
- Add advanced report date filters.
- Add CI/CD pipeline.
- Add scheduled database backups.
- Add HTTPS/domain setup for VPS.

## Assumptions

- Single supermarket location for V1.2.
- INR currency.
- GST-inclusive selling price.
- Aiven MySQL is the primary production database.
- Cashier workflows prioritize speed over configuration depth.
- Admin workflows prioritize full business visibility.
- USB barcode scanners behave as keyboard input.
- Camera barcode scanning depends on browser support and secure context.
- Fresh produce may use PLU codes rather than manufacturer EAN codes.
