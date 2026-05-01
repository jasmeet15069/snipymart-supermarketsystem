# SnipyMart Supermarket ERP + POS Final Closed-Scope PRD

## 1. Product Overview

SnipyMart is a supermarket ERP + POS platform for small and medium grocery/supermarket businesses. The product is designed for daily cashier operations, inventory control, purchase management, customer loyalty, sales reporting, and owner/admin oversight.

The system is built as a full-stack monorepo:

`C:\Users\ACXIOM\Desktop\Acxiom Files\Azure AI Foundry\erpsystem`

Final release scope: **V1.2 Closed Scope**

Primary deployments:

- Vercel: `https://snipymart-supermarketsystem.vercel.app`
- VPS frontend: `http://45.79.124.28:3001`
- VPS backend: `http://45.79.124.28:8010`
- GitHub: `https://github.com/jasmeet15069/snipymart-supermarketsystem`
- Database: Aiven MySQL

## 2. Product Vision

SnipyMart should feel like practical supermarket software, not a demo CRUD app. A cashier should be able to bill products quickly, an owner should understand sales and stock health, and an admin should be able to maintain products, suppliers, users, and inventory without touching the database.

The final product vision is a complete single-store supermarket ERP + POS covering POS billing, inventory, purchases, customers, users, barcode lookup, GST-aware sales, returns, and business reporting. No additional feature modules are planned beyond this closed scope unless a critical operational, security, compliance, or data-integrity need appears.

## 2.1 Closed Scope Statement

This PRD defines the final approved product scope for SnipyMart.

After this PRD, work should be limited to:

- Bug fixes.
- Security fixes.
- Deployment reliability fixes.
- Data integrity fixes.
- Performance fixes.
- Documentation corrections.
- Minor UI clarity fixes that do not introduce new business modules.
- Mandatory changes caused by hosting, database, browser, framework, or compliance requirements.

Work should not add new product modules or major new workflows unless explicitly re-approved as a necessary change.

## 3. Goals

### Business Goals

- Reduce billing time at the counter.
- Prevent stock mismatches and negative stock.
- Track every sale, purchase, return, and stock movement.
- Give owners clear visibility into revenue, low stock, and top products.
- Support realistic GST-inclusive pricing workflows.
- Provide a deployable, maintainable final system for single-store supermarket operations.

### Product Goals

- Build a usable POS-first workflow.
- Maintain normalized database structure.
- Keep transaction logic centralized in backend services.
- Make the frontend easy for non-technical store staff.
- Support barcode-based product lookup.
- Provide realistic seed data for demos and testing.
- Deploy reliably to Vercel and VPS.

### Technical Goals

- Use a modular FastAPI backend.
- Use Next.js App Router and TypeScript frontend.
- Use Aiven MySQL as production database.
- Keep secrets out of Git.
- Use migrations for schema changes.
- Keep business logic out of UI components.
- Keep the system maintainable without requiring further feature expansion.

## 4. Target Users

### Admin / Store Owner

Responsibilities:

- Manage products and prices.
- Manage inventory.
- Review sales reports.
- Manage suppliers and purchases.
- Manage customers.
- Manage users and cashier access.

Primary needs:

- Accurate business data.
- Clear dashboards.
- Low-stock visibility.
- Control over product catalog and pricing.
- User/role control.

### Cashier

Responsibilities:

- Open shift.
- Scan/search products.
- Create bills.
- Collect payments.
- Print/generate invoices.
- Handle basic returns.

Primary needs:

- Fast POS screen.
- Minimal clicks.
- Barcode support.
- Clear cart totals.
- Payment mode selection.
- Reliable stock validation.

### Inventory/Purchase Staff

Responsibilities:

- Receive goods.
- Track supplier orders.
- Check stock levels.
- Monitor expiry/batches.

Primary needs:

- Purchase order and GRN workflow.
- Batch/expiry visibility.
- Stock movement traceability.

## 5. Scope

### Final In Scope

- Single supermarket location.
- Product and category management.
- Inventory tracking.
- Batch and expiry fields.
- Stock movement history.
- POS billing.
- Barcode/manual lookup.
- GST and discounts.
- Cash, UPI, and card payments.
- Sales history.
- Basic reports.
- Supplier management.
- Purchase orders.
- Goods received notes.
- Customer management.
- Loyalty ledger.
- Cashier shifts.
- Admin/Cashier roles.
- JWT authentication.
- Seeded business data.
- Vercel and VPS deployments.

### Permanently Out of Scope Unless Re-Approved as Necessary

- Multi-branch inventory.
- Accounting ledger integration.
- Full GST return filing.
- Vendor payment reconciliation.
- Advanced promotion engine.
- Offline-first POS sync.
- Mobile app.
- Hardware printer integration beyond browser print styling.
- Automated stock forecasting.
- Warehouse transfers.

## 6. Current Build Status

### Completed

The following has been implemented and verified:

- Backend FastAPI project.
- Frontend Next.js project.
- Aiven MySQL database integration.
- Vercel deployment with backend services.
- VPS Docker deployment.
- Authentication and roles.
- Products, categories, inventory, suppliers, purchases, customers, users.
- POS screen.
- Sales and returns.
- Reports/dashboard APIs.
- Stock movements.
- Cashier shifts.
- Loyalty points.
- Realistic seed data.
- Verified product barcode data.
- `PRD.md`.
- `docs/barcode-sources.md`.

### Documentation Status

This document is the final closed-scope PRD. Any later changes should be treated as amendments, not as planned feature roadmap items.

## 7. Functional Requirements

## 7.1 Authentication and Authorization

### Must Have

- Users can log in with email/password.
- Backend issues JWT access and refresh tokens.
- Frontend stores tokens and attaches them to API requests.
- Admin and Cashier roles are supported.
- Protected frontend routes require login.
- Unauthorized API calls return proper errors.

### Current Status

Implemented.

### Acceptance Criteria

- Admin can log in and access all modules.
- Cashier can log in and access POS-related modules.
- Invalid credentials fail.
- Token refresh works.
- Protected pages redirect unauthenticated users.

## 7.2 Product and Category Management

### Must Have

- Admin can create, view, update, and deactivate products.
- Products support name, SKU, barcode, brand, HSN code, category, selling price, cost price, GST rate, unit, shelf location, and active status.
- Categories support GST defaults.
- Product lookup supports barcode, SKU, name, brand, HSN, and shelf location.

### Current Status

Implemented.

### Acceptance Criteria

- Product appears in POS after creation.
- Barcode lookup returns the correct product.
- Inactive products are excluded from normal POS lookup.
- Product table shows useful inventory/business fields.

## 7.3 Barcode Management

### Must Have

- Each packaged product can store a barcode.
- POS can find products by barcode.
- Manual barcode entry is supported.
- USB scanner input is supported as keyboard input.
- Camera scanner is supported where browser/device permissions allow it.

### Current Status

Implemented.

Verified barcodes are seeded for demo products. Examples:

```text
8901262260121 - Amul Taaza Toned Milk 1L
8901719113390 - Parle-G Gold Biscuits 250g
8901764012273 - Coca-Cola Original Taste 750ml
8904043901015 - Tata Salt 1kg
8901262010023 - Amul Salted Butter 500g
4011          - Robusta Banana PLU
```

### Acceptance Criteria

- Searching/scanning `8901262260121` returns Amul Taaza Toned Milk 1L.
- Searching/scanning `8901719113390` returns Parle-G Gold Biscuits 250g.
- Searching/scanning `4011` returns Robusta Banana 1kg.
- Unknown barcode shows a clear not-found state.

## 7.4 Inventory Management

### Must Have

- Track on-hand stock.
- Track reorder level.
- Track safety stock.
- Support inventory batches.
- Support expiry dates.
- Show low-stock products.
- Record stock movement for every sale, return, purchase receipt, and adjustment.
- Prevent negative stock.

### Current Status

Implemented for core stock, batches, movements, and low-stock fields.

### Acceptance Criteria

- Sale reduces inventory.
- GRN increases inventory.
- Return restores inventory.
- Stock movement is created for each stock change.
- Product with insufficient stock cannot be sold.

## 7.5 POS Billing

### Must Have

- Cashier can search products.
- Cashier can scan/enter barcodes.
- Cashier can add products to cart.
- Cart supports quantity and discount.
- System calculates subtotal, tax, discount, total, paid amount, balance, and change.
- Supports cash, UPI, and card.
- Sale is stored with immutable line snapshots.
- Stock is deducted after sale.
- Invoice/receipt data is generated.

### Current Status

Implemented.

### Acceptance Criteria

- Cashier can complete a sale with available stock.
- Sale persists in sales history.
- Payment persists.
- Stock decreases.
- Receipt can be viewed/printed.
- Cashier cannot sell more than available quantity.

## 7.6 Cashier Shifts

### Must Have

- Cashier can open shift.
- System can retrieve current shift.
- Cash sales are tied to shift workflow.
- Shift close endpoint exists.

### Current Status

Implemented.

### Acceptance Criteria

- Current open shift appears in POS.
- Cash sale requires a valid shift where enforced.
- Shift state is visible to cashier.

## 7.7 Sales and Returns

### Must Have

- Sales are persisted.
- Sale items are persisted.
- Payments are persisted.
- Sale returns can be created.
- Returns validate returnable quantity.
- Returns restore stock.
- Loyalty points are adjusted on return.

### Current Status

Implemented.

### Acceptance Criteria

- Sale appears in sales list.
- Return cannot exceed sold quantity.
- Returned items increase stock.
- Return record is linked to original sale.

## 7.8 Suppliers and Purchases

### Must Have

- Admin can manage suppliers.
- Admin can create purchase orders.
- Purchase orders contain product line items.
- Goods receipt updates received quantities.
- GRN increases inventory.
- Purchase order status changes when partially/fully received.

### Current Status

Implemented.

### Acceptance Criteria

- Purchase order can be created.
- GRN can be created from purchase order.
- Inventory increases after GRN.
- Supplier transaction data remains linked.

## 7.9 Customers and Loyalty

### Must Have

- Customer CRUD.
- Customer phone/email/address fields.
- Loyalty points.
- Loyalty tier.
- Customer purchase history.
- Loyalty ledger.

### Current Status

Implemented.

### Acceptance Criteria

- Customer can be selected in POS.
- Sale updates customer purchase history.
- Loyalty points are updated after sale.
- Return reverses/adjusts points where applicable.

## 7.10 Reports and Dashboard

### Must Have

- Dashboard KPIs.
- Revenue summary.
- Top products.
- Low-stock indicators.
- Sales reports.

### Current Status

Implemented at basic analytics level.

### Acceptance Criteria

- Dashboard loads without errors.
- Revenue API returns values.
- Top products API returns ranked products.
- Reports reflect stored transaction data.

## 7.11 User Management

### Must Have

- Admin can create users.
- Admin can assign role.
- Admin can view existing users.
- Users have active/inactive state.

### Current Status

Implemented and fixed.

### Acceptance Criteria

- Users page shows seeded users.
- Admin can add cashier.
- Cashier login works after user creation.

## 8. Non-Functional Requirements

## 8.1 Performance

### Requirements

- POS product lookup should feel instant for normal store catalog size.
- Barcode lookup should return within acceptable billing workflow time.
- Dashboard should load without blocking POS operations.
- API queries should use limits/pagination where needed.

### Current Status

Basic performance is acceptable for V1.2 seed and demo scale.

## 8.2 Security

### Requirements

- Secrets must not be committed.
- JWT tokens must be required for protected APIs.
- Passwords must be hashed.
- CORS must be restricted to known frontend origins.
- Database credentials must stay in environment variables.

### Current Status

Implemented.

## 8.3 Reliability

### Requirements

- POS sale should be transactional.
- Inventory should not become negative.
- Failed sale should not partially deduct stock.
- Migration history should be preserved.

### Current Status

Core transactional service logic is implemented.

## 8.4 Maintainability

### Requirements

- Backend code should remain modular.
- Business logic should live in services.
- Frontend API client should be centralized.
- Database changes should go through Alembic.

### Current Status

Implemented.

## 8.5 Deployment

### Requirements

- App can run locally.
- App can deploy to Vercel.
- App can deploy to VPS with Docker.
- Environment variables can be configured per environment.

### Current Status

Implemented and verified.

## 9. Data Requirements

### Core Data

- Users
- Products
- Categories
- Inventory items
- Inventory batches
- Stock movements
- Sales
- Sale items
- Payments
- Sale returns
- Suppliers
- Purchase orders
- Goods receipts
- Customers
- Loyalty ledger
- Cashier shifts

### Data Integrity Rules

- Product SKU should be unique.
- Barcode should identify products for POS lookup.
- Stock cannot go negative.
- Sale line snapshots should not change when product price changes later.
- Every stock mutation should create a movement record.
- Returns must reference original sale.

## 10. Release Status

## V1.0

Released:

- Initial full-stack ERP/POS foundation.
- Backend and frontend deployment.
- Core modules.

## V1.2

Released:

- Improved POS.
- Barcode scanner/manual lookup.
- Users visibility fix.
- Hydration warning mitigation.
- Business table enhancements.
- Better seed data.
- Vercel services deployment.
- Vercel backend environment fix.
- Verified product barcode seed data.
- PRD documentation.

## 11. Maintenance Policy

There is no planned feature roadmap after this final PRD.

Allowed post-final work:

- Fix login, billing, inventory, purchasing, reporting, deployment, or data issues.
- Fix security vulnerabilities.
- Fix database migration or seed-data problems.
- Keep dependencies compatible when required.
- Improve reliability of already-approved workflows.
- Improve documentation accuracy.
- Adjust deployment configuration when hosting providers require it.

Not allowed without explicit re-approval:

- Adding multi-store support.
- Adding offline POS mode.
- Adding accounting modules.
- Adding mobile apps.
- Adding a new promotion engine.
- Adding new major reports outside the existing reporting module.
- Adding new hardware workflows beyond existing browser/manual/USB barcode support.
- Adding new role systems beyond Admin and Cashier.

## 12. Open Risks

- Camera barcode scanning depends on browser support, HTTPS, and permissions.
- Public barcode records may vary by region/packaging.
- Fresh produce often uses PLU or store-generated labels, not manufacturer EAN.
- Vercel serverless backend can have cold starts.
- Direct MySQL from serverless may need connection-pooling strategy at scale.
- Reporting is intentionally limited to the approved dashboard/reporting scope.
- Legacy backup table should only be dropped after explicit approval.

## 13. Closed Product Decisions

- Single-store scope is final.
- Admin and Cashier roles are final.
- Existing POS discount behavior is final.
- Existing loyalty earn/ledger behavior is final.
- Existing supplier and purchase-order workflow is final.
- Existing barcode/manual/USB/camera scanner support is final.
- Existing invoice/receipt browser print support is final.
- Vercel and VPS deployment support are both accepted.
- Any future change must be classified as necessary maintenance or explicitly approved as a scope amendment.

## 14. Acceptance Checklist

### Final Feature Acceptance

- [x] Admin can log in.
- [x] Cashier can log in.
- [x] Protected routes work.
- [x] Products load.
- [x] Inventory loads.
- [x] POS loads.
- [x] Barcode lookup works.
- [x] Sale flow works.
- [x] Stock is updated after sale.
- [x] Purchase order and GRN flow exists.
- [x] Customers and loyalty exist.
- [x] Users page works.
- [x] Dashboard/reports load.
- [x] Vercel backend health works.
- [x] Vercel login works.
- [x] VPS containers run.
- [x] GitHub is synced.
- [x] Seed data is business-realistic.
- [x] Barcode source documentation exists.

### Final Closed-Scope Acceptance

- [x] Product scope is closed.
- [x] No future feature roadmap is included.
- [x] Post-final work is limited to fixes, maintenance, security, deployment, data integrity, and documentation.
- [x] Major new modules require explicit re-approval.

## 15. Final Recommendation

SnipyMart V1.2 Closed Scope is the final approved version of the supermarket ERP + POS product.

The product should now be treated as complete for the agreed feature scope. Future work should not add new features unless necessary for:

- Bug resolution.
- Security.
- Deployment stability.
- Database/data integrity.
- Compliance.
- Compatibility with required infrastructure changes.

Any requested expansion beyond these categories should be handled as a formal scope amendment, not as continuation of this PRD.
