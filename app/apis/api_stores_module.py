from fastapi import APIRouter, HTTPException, Path, Body, status, FastAPI
from typing import List, Optional
from datetime import datetime

# Assuming models are in a sibling 'models' directory, adjust if structure differs
from ..models.models_stores_module import Store, StoreCreate # StoreBase is implicitly handled by StoreCreate

# Mock Database for Stores Module
# IMPORTANT: When integrated into main_api.py, this local mock_db will be
# superseded by the shared_mock_db instance from main_api.py.
mock_db_stores_module = {
    "stores": {},
    # StoreID is string and user-provided/generated, so no simple 'next_store_id' counter here.
    # Uniqueness of StoreID will be checked.
}

router = APIRouter(
    prefix="/api/v1",
    tags=["Stores Module"]
)

# --- Stores Endpoints ---

@router.post("/stores", response_model=Store, status_code=status.HTTP_201_CREATED)
async def create_store_endpoint(store_in: StoreCreate = Body(...)):
    # Using mock_db_stores_module for this module's data, which will be patched to shared_mock_db
    db_to_use = mock_db_stores_module # In main_api, this variable itself will point to shared_mock_db

    if store_in.storeID in db_to_use["stores"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Store ID '{store_in.storeID}' already exists.")

    # Check for unique prefixes if they are set
    if store_in.cashPrefix and any(s.cashPrefix == store_in.cashPrefix for s in db_to_use["stores"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CashPrefix '{store_in.cashPrefix}' already in use.")
    if store_in.laybyPrefix and any(s.laybyPrefix == store_in.laybyPrefix for s in db_to_use["stores"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"LaybyPrefix '{store_in.laybyPrefix}' already in use.")
    if store_in.fieldPrefix and any(s.fieldPrefix == store_in.fieldPrefix for s in db_to_use["stores"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"FieldPrefix '{store_in.fieldPrefix}' already in use.")

    new_store = Store(
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        **store_in.model_dump()
    )
    db_to_use["stores"][new_store.storeID] = new_store
    return new_store

@router.get("/stores", response_model=List[Store])
async def get_all_stores_endpoint(
    skip: int = 0,
    limit: int = 10,
    is_active: Optional[bool] = None,
    store_type: Optional[str] = None,
    name: Optional[str] = None
):
    db_to_use = mock_db_stores_module
    results = list(db_to_use["stores"].values())
    if is_active is not None:
        results = [s for s in results if s.isActive == is_active]
    if store_type:
        results = [s for s in results if s.storeType.lower() == store_type.lower()]
    if name:
        results = [s for s in results if name.lower() in s.storeName.lower()]
    return results[skip : skip + limit]

@router.get("/stores/{store_id}", response_model=Store)
async def get_store_by_id_endpoint(store_id: str = Path(..., title="The ID of the store", min_length=1, max_length=10)):
    db_to_use = mock_db_stores_module
    store = db_to_use["stores"].get(store_id)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")
    return store

@router.put("/stores/{store_id}", response_model=Store)
async def update_store_endpoint(
    store_id: str = Path(..., title="The ID of the store to update", min_length=1, max_length=10),
    store_in: StoreCreate = Body(...) # Using StoreCreate for update, implies all fields can be updated
                                      # A StoreUpdate model might exclude storeID from body
):
    db_to_use = mock_db_stores_module
    if store_id not in db_to_use["stores"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    # If store_in.storeID is different from path store_id, it implies changing PK, which is complex.
    # For simplicity, we assume storeID in path is the target, and storeID in body must match or is ignored.
    if store_in.storeID != store_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Store ID in path does not match Store ID in body. Cannot change Store ID.")

    current_store = db_to_use["stores"][store_id]

    # Check for unique prefixes if they are set and changed
    if store_in.cashPrefix and store_in.cashPrefix != current_store.cashPrefix and \
       any(s.cashPrefix == store_in.cashPrefix for s_id, s in db_to_use["stores"].items() if s_id != store_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CashPrefix '{store_in.cashPrefix}' already in use.")
    if store_in.laybyPrefix and store_in.laybyPrefix != current_store.laybyPrefix and \
       any(s.laybyPrefix == store_in.laybyPrefix for s_id, s in db_to_use["stores"].items() if s_id != store_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"LaybyPrefix '{store_in.laybyPrefix}' already in use.")
    if store_in.fieldPrefix and store_in.fieldPrefix != current_store.fieldPrefix and \
       any(s.fieldPrefix == store_in.fieldPrefix for s_id, s in db_to_use["stores"].items() if s_id != store_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"FieldPrefix '{store_in.fieldPrefix}' already in use.")

    updated_data = store_in.model_dump(exclude_unset=True)
    updated_store = current_store.model_copy(update=updated_data)
    updated_store.updatedAt = datetime.utcnow()
    db_to_use["stores"][store_id] = updated_store
    return updated_store

@router.delete("/stores/{store_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_store_endpoint(store_id: str = Path(..., title="The ID of the store to delete", min_length=1, max_length=10)):
    db_to_use = mock_db_stores_module
    if store_id not in db_to_use["stores"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Store not found")

    # In a real app, check if store is linked to transactions, inventory, users, etc.
    # For example (conceptual check):
    # if any(invoice.storeID == store_id for invoice in shared_mock_db.get("sales_invoice_headers", {}).values()):
    #     raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Store is in use by sales invoices and cannot be deleted. Consider deactivating instead.")
    # Similar checks for products (if they have a primary store), stock entries, etc.

    del db_to_use["stores"][store_id]
    # No return for 204 status

# For standalone testing of this module
if __name__ == "__main__":
    app_stores_test_standalone = FastAPI(title="ERP Stores Module API - Standalone Test")
    app_stores_test_standalone.include_router(router)
    import uvicorn
    print("Starting Uvicorn server for Stores API (Standalone Test)...")
    print("Access OpenAPI docs at http://127.0.0.1:8006/docs") # Use a different port
    uvicorn.run(app_stores_test_standalone, host="127.0.0.1", port=8006, reload=False)

```

**Explanation of `app/apis/api_stores_module.py`:**

1.  **Imports:** FastAPI components and Pydantic models (`Store`, `StoreCreate`) from `models_stores_module.py`.
2.  **Mock Database (`mock_db_stores_module`):**
    *   A local dictionary to simulate data storage for stores.
    *   Since `StoreID` is a user-provided string (e.g., "SH01"), there's no simple `next_store_id` integer counter; uniqueness of `StoreID` is checked during creation.
3.  **APIRouter:** Organizes store-related routes.
4.  **Stores Endpoints (CRUD for `/stores`):**
    *   **`POST /stores`**: Creates a new store.
        *   Validates uniqueness of `storeID`.
        *   Validates uniqueness of `cashPrefix`, `laybyPrefix`, `fieldPrefix` if they are provided (as these were defined as UNIQUE in the SQL DDL).
    *   **`GET /stores`**: Lists stores with basic filtering (by `is_active`, `store_type`, `name`) and pagination.
    *   **`GET /stores/{store_id}`**: Retrieves a specific store by its `storeID`.
    *   **`PUT /stores/{store_id}`**: Updates an existing store.
        *   Ensures `storeID` in the path matches `storeID` in the request body (prevents changing the PK via this endpoint).
        *   Includes uniqueness checks for prefixes if they are changed.
    *   **`DELETE /stores/{store_id}`**: Deletes a store. Includes a placeholder comment about checking for linked entities (like invoices, inventory) before allowing deletion in a real application.
5.  **Path Parameter Validation:** `store_id` in paths now includes `min_length=1, max_length=10` to match the `VARCHAR(10)` definition.
6.  **`db_to_use` Variable:** Inside each endpoint, `db_to_use = mock_db_stores_module` is used. When `main_api.py` monkey-patches `mock_db_stores_module` to point to `shared_mock_db`, all these endpoints will correctly operate on the shared data store.
7.  **Standalone Runner:** Includes `if __name__ == "__main__":` for isolated testing on port 8006.

This file `app/apis/api_stores_module.py` provides the structural API for managing Stores.

This completes the third step of the current plan.
