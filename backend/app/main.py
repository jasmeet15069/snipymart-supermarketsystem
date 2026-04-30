from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.errors import register_error_handlers
from app.core.logging import configure_logging
from app.routes import auth, categories, customers, inventory, products, purchases, reports, sales, shifts, suppliers, users

configure_logging()

app = FastAPI(title=settings.app_name, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


for router in [
    auth.router,
    users.router,
    categories.router,
    products.router,
    inventory.router,
    sales.router,
    shifts.router,
    suppliers.router,
    purchases.router,
    customers.router,
    reports.router,
]:
    app.include_router(router, prefix=settings.api_v1_prefix)
