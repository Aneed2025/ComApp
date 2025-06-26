from fastapi import FastAPI
from datetime import datetime

# Import routers and initial mock_db structures from module-specific API files
from .apis.api_product_module import router as products_router
from .apis.api_product_module import mock_db as product_module_mock_db_init

from .apis.api_customer_module import router as customers_router
from .apis.api_customer_module import mock_db_customer_module as customer_module_mock_db_init

from .apis.api_supplier_module import router as suppliers_router
from .apis.api_supplier_module import mock_db_supplier_module as supplier_module_mock_db_init

from .apis.api_discount_module import router as discounts_router
from .apis.api_discount_module import mock_db_discount_module as discount_module_mock_db_init

from .apis.api_sales_module import router as sales_router
from .apis.api_sales_module import db as sales_module_db_alias # api_sales_module uses 'db' internally

from .apis.api_stores_module import router as stores_router
from .apis.api_stores_module import mock_db_stores_module as stores_module_mock_db_init
from .apis.api_purchase_orders_module import router as purchase_orders_router # PO import
from .apis.api_purchase_orders_module import db as purchase_orders_module_mock_db_init # PO import for mock_db
from .apis.api_grn_module import router as grn_router # New GRN import
from .apis.api_grn_module import db as grn_module_mock_db_init # New GRN import for mock_db


app = FastAPI(
    title="ERP System API - Consolidated",
    version="0.1.10", # Incremented version for GRN module
    description="Consolidated API for Products, Customers, Suppliers, Discounts, Sales, Stores, Purchase Orders, and GRNs. " \
                "Uses a shared in-memory mock database for demonstration."
)

# --- Consolidated Mock In-Memory Database ---
shared_mock_db = {
    # Product Module Data & Counters
    "categories": product_module_mock_db_init["categories"],
    "products": product_module_mock_db_init["products"],
    "product_images": product_module_mock_db_init["product_images"],
    "next_category_id": product_module_mock_db_init["next_category_id"],
    "next_product_id": product_module_mock_db_init["next_product_id"],
    "next_product_image_id": product_module_mock_db_init["next_product_image_id"],

    # Customer Module Data & Counters
    "customer_groups": customer_module_mock_db_init["customer_groups"],
    "customers": customer_module_mock_db_init["customers"],
    "next_customer_group_id": customer_module_mock_db_init["next_customer_group_id"],
    "next_customer_id": customer_module_mock_db_init["next_customer_id"],

    # Supplier Module Data & Counters
    "suppliers": supplier_module_mock_db_init["suppliers"],
    "supplier_products": supplier_module_mock_db_init["supplier_products"],
    "next_supplier_id": supplier_module_mock_db_init["next_supplier_id"],
    "next_supplier_product_id": supplier_module_mock_db_init["next_supplier_product_id"],

    # Discount Module Data & Counters
    "discounts": discount_module_mock_db_init["discounts"],
    "product_discounts": discount_module_mock_db_init["product_discounts"],
    "discount_store_applicability": discount_module_mock_db_init["discount_store_applicability"],
    "discount_customer_group_applicability": discount_module_mock_db_init["discount_customer_group_applicability"],
    "next_discount_id": discount_module_mock_db_init["next_discount_id"],
    "next_product_discount_id": discount_module_mock_db_init["next_product_discount_id"],
    "next_discount_store_applicability_id": discount_module_mock_db_init["next_discount_store_applicability_id"],
    "next_discount_customer_group_applicability_id": discount_module_mock_db_init["next_discount_customer_group_applicability_id"],

    # Sales Module Data & Counters
    "sales_invoice_headers": sales_module_db_alias.get("sales_invoice_headers", {}),
    "sales_invoice_lines": sales_module_db_alias.get("sales_invoice_lines", {}),
    "next_sales_invoice_line_id": sales_module_db_alias.get("next_sales_invoice_line_id", 1),
    # Note: next_sales_invoice_header_id_counter is managed within api_sales_module directly using shared_mock_db
    # So, we don't need to initialize it here from its local mock, but ensure it's added if not present
    "next_sales_invoice_header_id_counter": sales_module_db_alias.get("next_sales_invoice_header_id_counter", {}),


    # Stores Module Data
    "stores": stores_module_mock_db_init["stores"],
    # next_store_id_numeric is managed within api_stores_module for formatted StoreID

    # Purchase Orders Module Data & Counters
    "purchase_order_headers": purchase_orders_module_mock_db_init.get("purchase_order_headers", {}),
    "purchase_order_lines": purchase_orders_module_mock_db_init.get("purchase_order_lines", {}),
    "next_po_header_id_counter": purchase_orders_module_mock_db_init.get("next_po_header_id_counter", {}),
    "next_po_line_id": purchase_orders_module_mock_db_init.get("next_po_line_id", 1),

    # GRN Module Data & Counters (New)
    "goods_receipt_note_headers": grn_module_mock_db_init.get("goods_receipt_note_headers", {}),
    "goods_receipt_note_lines": grn_module_mock_db_init.get("goods_receipt_note_lines", {}),
    "next_grn_header_id_counter": grn_module_mock_db_init.get("next_grn_header_id_counter", {}),
    "next_grn_line_id": grn_module_mock_db_init.get("next_grn_line_id", 1),
}

# --- "Monkey-Patch" Module-Level Mock DBs to use shared_mock_db ---
from .apis import api_product_module
from .apis import api_customer_module
from .apis import api_supplier_module
from .apis import api_discount_module
from .apis import api_sales_module
from .apis import api_stores_module
from .apis import api_purchase_orders_module # PO import for patching
from .apis import api_grn_module # New GRN import for patching

api_product_module.mock_db = shared_mock_db
api_customer_module.mock_db_customer_module = shared_mock_db
api_supplier_module.mock_db_supplier_module = shared_mock_db
api_discount_module.mock_db_discount_module = shared_mock_db
api_sales_module.db = shared_mock_db
api_stores_module.mock_db_stores_module = shared_mock_db
api_purchase_orders_module.db = shared_mock_db # Patched 'db' in api_purchase_orders_module
api_grn_module.db = shared_mock_db # New patch for GRN module

# --- Include Routers from each module ---
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(suppliers_router)
app.include_router(discounts_router)
app.include_router(sales_router)
app.include_router(stores_router)
app.include_router(purchase_orders_router) # PO router included
app.include_router(grn_router) # New GRN router included

# --- Root Endpoint for the Main API ---
@app.get("/")
async def root_endpoint():
    return {
        "message": "Welcome to the ERP System API (Consolidated v0.1.10)",
        "documentation_url": "/docs",
        "redoc_url": "/redoc",
        "active_modules_prefix": "/api/v1",
        "available_modules": ["Products", "Customers", "Suppliers", "Discounts", "Sales", "Stores", "PurchaseOrders", "GRNs"]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting main Uvicorn server for the consolidated ERP API...")
    print("Access OpenAPI (Swagger UI) documentation at http://127.0.0.1:8000/docs")
    print("Access ReDoc documentation at http://127.0.0.1:8000/redoc")

    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
```

**Summary of changes in `app/main_api.py`:**

1.  **Import Stores Router and Mock DB:** Added imports for `router as stores_router` and `mock_db_stores_module as stores_module_mock_db_init` from `api_stores_module.py`.
2.  **Extend `shared_mock_db`:** Added a new key `"stores"` to `shared_mock_db`, initialized from `stores_module_mock_db_init["stores"]`.
3.  **Monkey-Patch Stores Module's DB Variable:** Added `api_stores_module.mock_db_stores_module = shared_mock_db` to ensure the stores API endpoints operate on the shared database.
4.  **Include Stores Router:** Added `app.include_router(stores_router)` to make the stores API endpoints accessible.
5.  **Updated Root Endpoint Message:** Updated the version and added "Stores" to the list of available modules.
6.  **Sales Module Mock DB Init:** Used `.get()` for sales module keys from its `db` alias for safety during initialization of `shared_mock_db`, in case those keys weren't pre-defined in `api_sales_module.py`'s local `mock_db_sales_module` (though they were).

With these changes, the `main_api.py` now incorporates the new Stores API module, and all implemented modules should be using the same shared in-memory mock database. The application should be runnable, and the Stores API endpoints testable.

This completes the fourth step of the current plan.
