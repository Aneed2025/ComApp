<<<<<<< HEAD

=======
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
from fastapi import FastAPI
from datetime import datetime

# Assuming apis and models are subdirectories of the 'app' directory,
# and this main_api.py is also in the 'app' directory.
<<<<<<< HEAD
from .apis.api_product_module import router as products_router
from .apis.api_product_module import mock_db as product_module_mock_db_init 
=======
# Adjust imports if your structure is different (e.g., if main_api.py is one level above 'app')

# It's generally better if the API modules don't define their own mock_db instances
# but instead expect a 'db' dependency or import a shared db instance.
# For this iteration, we are importing their mock_db initial structures and then
# redirecting their module-level 'mock_db' variable to our shared_mock_db.

from .apis.api_product_module import router as products_router
from .apis.api_product_module import mock_db as product_module_mock_db_init
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b

from .apis.api_customer_module import router as customers_router
from .apis.api_customer_module import mock_db_customer_module as customer_module_mock_db_init

from .apis.api_supplier_module import router as suppliers_router
from .apis.api_supplier_module import mock_db_supplier_module as supplier_module_mock_db_init

app = FastAPI(
<<<<<<< HEAD
    title="ERP System API - Corrected Structure",
    version="0.1.5", 
=======
    title="ERP System API - Consolidated",
    version="0.1.3", # Incremented version
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
    description="Consolidated API for Products, Customers, and Suppliers modules for an ERP system. "\
                "Uses a shared in-memory mock database for demonstration."
)

# --- Consolidated Mock In-Memory Database ---
shared_mock_db = {
<<<<<<< HEAD
    # Product Module Data & Counters
=======
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
    "categories": product_module_mock_db_init["categories"],
    "products": product_module_mock_db_init["products"],
    "product_images": product_module_mock_db_init["product_images"],
    "next_category_id": product_module_mock_db_init["next_category_id"],
    "next_product_id": product_module_mock_db_init["next_product_id"],
    "next_product_image_id": product_module_mock_db_init["next_product_image_id"],
<<<<<<< HEAD
    
    # Customer Module Data & Counters
=======

>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
    "customer_groups": customer_module_mock_db_init["customer_groups"],
    "customers": customer_module_mock_db_init["customers"],
    "next_customer_group_id": customer_module_mock_db_init["next_customer_group_id"],
    "next_customer_id": customer_module_mock_db_init["next_customer_id"],
<<<<<<< HEAD
    
    # Supplier Module Data & Counters
=======

>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
    "suppliers": supplier_module_mock_db_init["suppliers"],
    "supplier_products": supplier_module_mock_db_init["supplier_products"],
    "next_supplier_id": supplier_module_mock_db_init["next_supplier_id"],
    "next_supplier_product_id": supplier_module_mock_db_init["next_supplier_product_id"],
}

# --- "Monkey-Patch" Module-Level Mock DBs to use shared_mock_db ---
<<<<<<< HEAD
from .apis import api_product_module 
from .apis import api_customer_module
from .apis import api_supplier_module

api_product_module.mock_db = shared_mock_db 
api_customer_module.mock_db_customer_module = shared_mock_db 
api_supplier_module.mock_db_supplier_module = shared_mock_db 
=======
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
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b

# --- Include Routers from each module ---
app.include_router(products_router)
app.include_router(customers_router)
app.include_router(suppliers_router)

# --- Root Endpoint for the Main API ---
@app.get("/")
async def root_endpoint():
    return {
<<<<<<< HEAD
        "message": "Welcome to the ERP System API (Corrected Structure v0.1.5)",
=======
        "message": "Welcome to the ERP System API (Consolidated v0.1.3)",
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
        "documentation_url": "/docs",
        "redoc_url": "/redoc",
        "active_modules_prefix": "/api/v1"
    }

# --- Uvicorn Runner (for convenience when running this file directly) ---
<<<<<<< HEAD
if __name__ == "__main__":
=======
# To run from the directory containing the 'app' folder (e.g., erp_project/):
# uvicorn app.main_api:app --reload
# Or if you are inside the 'app' folder:
# uvicorn main_api:app --reload (Python needs to find sibling 'apis' and 'models' packages)

if __name__ == "__main__":
    # This specific way of running is if main_api.py is executed directly
    # AND is in a location where Python can resolve the relative imports
    # (e.g. if 'app' is the current working directory or in PYTHONPATH).
    # The command `uvicorn app.main_api:app --reload` from parent of 'app' is more robust.
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
    import uvicorn
    print("Starting main Uvicorn server for the consolidated ERP API...")
    print("Ensure this script is run in a way that Python can resolve './apis' and './models' imports.")
    print("Typically, run from the parent directory of 'app' using: uvicorn app.main_api:app --reload")
    print("Access OpenAPI (Swagger UI) documentation at http://127.0.0.1:8000/docs")
    print("Access ReDoc documentation at http://127.0.0.1:8000/redoc")
<<<<<<< HEAD
    
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
=======

    # For direct execution `python main_api.py` from within `app` directory:
    uvicorn.run("main_api:app", host="127.0.0.1", port=8000, reload=True)
```
>>>>>>> 49d0fbfa0cda18a40014249d83f9fa5f79187d0b
