from fastapi import FastAPI
from datetime import datetime

# Assuming apis and models are subdirectories of the 'app' directory,
# and this main_api.py is also in the 'app' directory.
# These relative imports should work if main_api.py is run correctly
# (e.g. uvicorn app.main_api:app from parent directory of 'app')
from .apis.api_product_module import router as products_router
from .apis.api_product_module import mock_db as product_module_mock_db_init

from .apis.api_customer_module import router as customers_router
from .apis.api_customer_module import mock_db_customer_module as customer_module_mock_db_init

from .apis.api_supplier_module import router as suppliers_router
from .apis.api_supplier_module import mock_db_supplier_module as supplier_module_mock_db_init

app = FastAPI(
    title="ERP System API - Corrected Structure",
    version="0.1.5", # Incremented version
    description="Consolidated API for Products, Customers, and Suppliers modules for an ERP system. "\
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
}

# --- "Monkey-Patch" Module-Level Mock DBs to use shared_mock_db ---
# This makes the `mock_db` (or similarly named) variables inside each `api_*.py` file
# refer to the `shared_mock_db` defined here.
# All operations in those modules will now read from and write to this central store,
# including the 'next_..._id' counters.

# Need to import the modules themselves to modify their globals
from .apis import api_product_module
from .apis import api_customer_module
from .apis import api_supplier_module

api_product_module.mock_db = shared_mock_db
api_customer_module.mock_db_customer_module = shared_mock_db
api_supplier_module.mock_db_supplier_module = shared_mock_db

# --- Include Routers from each module ---
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(suppliers_router)

# --- Root Endpoint for the Main API ---
@app.get("/")
async def root_endpoint():
    return {
        "message": "Welcome to the ERP System API (Corrected Structure v0.1.5)",
        "documentation_url": "/docs",
        "redoc_url": "/redoc",
        "active_modules_prefix": "/api/v1"
    }

# --- Uvicorn Runner (for convenience when running this file directly) ---
# To run from the directory containing the 'app' folder (e.g., erp_project/):
# uvicorn app.main_api:app --reload
# Or if you are inside the 'app' folder (ensure PYTHONPATH allows sibling package imports):
# python main_api.py (if the __main__ block below is uncommented and uvicorn is importable)

if __name__ == "__main__":
    import uvicorn
    print("Starting main Uvicorn server for the consolidated ERP API...")
    print("Ensure this script is run in a way that Python can resolve './apis' and './models' imports.")
    print("Typically, run from the parent directory of 'app' using: uvicorn app.main_api:app --reload")
    print("Access OpenAPI (Swagger UI) documentation at http://127.0.0.1:8000/docs")
    print("Access ReDoc documentation at http://127.0.0.1:8000/redoc")

    # For direct execution `python main_api.py` from within `app` directory:
    # This requires that the parent of 'app' is in PYTHONPATH or you run as `python -m app.main_api` from parent.
    # The `uvicorn app.main_api:app --reload` from parent of `app` is more robust for package structures.
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
```
