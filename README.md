# SnipyMart ERP + POS

Production-oriented supermarket ERP and POS system built with FastAPI, Next.js App Router, TypeScript, Tailwind, SQLAlchemy, Alembic, and MySQL.

## Modules

- Product catalog with SKU, barcode, category, GST, cost, selling price, reorder level, and opening stock.
- FIFO batch inventory with expiry dates, stock movements, and low-stock alerts.
- POS billing with barcode/search lookup, cart, GST-inclusive pricing, discounts, payments, stock deduction, invoices, and transaction history.
- Sales reports, dashboard KPIs, revenue series, and top-selling products.
- Suppliers, purchase orders, partial GRN receiving, and stock increase on receipt.
- Customers, loyalty ledger support, and purchase history endpoint.
- JWT auth with Admin and Cashier roles.
- Cashier shift open/close and cash payment enforcement.
- Basic sale returns with batch restocking.

## Project Structure

```text
backend/
  app/core        config, db, auth, errors, logging
  app/models      SQLAlchemy domain models
  app/schemas     Pydantic API contracts
  app/crud        reusable persistence helpers
  app/services    transactional business workflows
  app/routes      FastAPI route modules
  alembic/        migration setup
frontend/
  src/app         Next.js pages
  src/components  app shell, providers, UI primitives
  src/lib         API client, types, formatting
```

## Backend Setup

```powershell
cd "C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem\backend"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Set `DATABASE_URL` in `backend\.env` to your Aiven MySQL URL. Keep the real password out of Git:

```text
mysql://avnadmin:<password>@mysql-3b9cb5b9-snipymart-390c.h.aivencloud.com:22157/defaultdb?ssl-mode=REQUIRED
```

Run migrations and seed data:

```powershell
python -m alembic upgrade head
python -m app.seed
python -m uvicorn app.main:app --reload --port 8000
```

Seeded accounts:

- Admin: `admin@snipymart.in` / `Admin@12345`
- Cashier: `cashier@snipymart.in` / `Cashier@12345`

## Frontend Setup

```powershell
cd "C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem\frontend"
npm install
Copy-Item .env.local.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Docker

```powershell
cd "C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem"
docker compose up --build
```

## V1 Server Deployment

The V1 production compose file avoids existing services on the target server:

- Frontend: `http://45.79.124.28:3001`
- Backend API: `http://45.79.124.28:8010/api/v1`

```bash
cd /opt/snipymart-supermarketsystem
docker compose -f docker-compose.prod.yml up -d --build
docker compose -f docker-compose.prod.yml exec backend python -m alembic upgrade head
docker compose -f docker-compose.prod.yml exec backend python -m app.seed
```

Optional local MySQL profile:

```powershell
docker compose --profile local-db up --build
```

For local MySQL, set:

```text
DATABASE_URL=mysql://erp:erp@mysql-local:3306/erpsystem
```

## Verification

```powershell
cd backend
python -m pytest -q

cd ..\frontend
npm run typecheck
npm run build
```

## Notes

- Shelf prices are GST-inclusive; invoices split taxable value and GST automatically.
- Cash sales require the cashier to have an open shift.
- Stock deduction uses FIFO batches and blocks negative stock.
- `.env` and `.env.local` are ignored so secrets stay out of source control.
