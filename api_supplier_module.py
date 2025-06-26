from fastapi import FastAPI, HTTPException, APIRouter, Path, Body, status
from typing import List, Optional
from datetime import datetime

# Assuming models_supplier_module.py and models_product_module.py (for Product IDs)
# are in the same directory or accessible in PYTHONPATH
from models_supplier_module import (
    Supplier, SupplierCreate,
    SupplierProduct, SupplierProductCreate
)
# We'll need Product IDs for SupplierProduct, so we'll assume a mock products store exists
# in the consolidated main_api.py. For now, we'll just use product IDs directly.

# Mock Database (this would ideally be a shared instance or a proper DB service)
# This will be part of a larger mock_db in main_api.py.
mock_db_supplier_module = {
    "suppliers": {},
    "supplier_products": {}, # Stores SupplierProduct link objects
    "next_supplier_id": 1,
    "next_supplier_product_id": 1,
}

# --- API Router for Suppliers Module ---
router = APIRouter(
    prefix="/api/v1",
    tags=["Suppliers Module"]
)

# --- Suppliers Endpoints ---

@router.post("/suppliers", response_model=Supplier, status_code=status.HTTP_201_CREATED)
async def create_supplier_endpoint(supplier_in: SupplierCreate):
    # --- DB Interaction Placeholder ---
    if any(s.supplierName.lower() == supplier_in.supplierName.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier name already exists")
    if supplier_in.taxID and \
       any(s.taxID and s.taxID.lower() == supplier_in.taxID.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TaxID already exists")
    if supplier_in.email and \
       any(s.email and s.email.lower() == supplier_in.email.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    new_id = mock_db_supplier_module["next_supplier_id"]
    supplier_data_for_db = supplier_in.model_dump()

    db_supplier = Supplier(
        supplierID=new_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        suppliedProducts=[], # Initialize with empty list
        **supplier_data_for_db
    )
    mock_db_supplier_module["suppliers"][new_id] = db_supplier
    mock_db_supplier_module["next_supplier_id"] += 1
    return db_supplier

@router.get("/suppliers", response_model=List[Supplier])
async def get_all_suppliers_endpoint(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    tax_id: Optional[str] = None,
    email: Optional[str] = None
):
    # --- DB Interaction Placeholder ---
    results = list(mock_db_supplier_module["suppliers"].values())
    if name:
        results = [s for s in results if name.lower() in s.supplierName.lower()]
    if tax_id:
        results = [s for s in results if s.taxID and tax_id.lower() == s.taxID.lower()]
    if email:
        results = [s for s in results if s.email and email.lower() == s.email.lower()]

    response_list = []
    for supplier_data in results[skip : skip + limit]:
        # Populate suppliedProducts for each supplier
        linked_products = [
            sp for sp in mock_db_supplier_module["supplier_products"].values()
            if sp.supplierID == supplier_data.supplierID
        ]
        temp_supplier_dict = supplier_data.model_dump()
        temp_supplier_dict['suppliedProducts'] = linked_products
        response_list.append(Supplier(**temp_supplier_dict))

    return response_list

@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier_by_id_endpoint(supplier_id: int = Path(..., title="The ID of the supplier to get")):
    # --- DB Interaction Placeholder ---
    supplier = mock_db_supplier_module["suppliers"].get(supplier_id)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    linked_products = [
        sp for sp in mock_db_supplier_module["supplier_products"].values()
        if sp.supplierID == supplier_id
    ]
    temp_supplier_dict = supplier.model_dump()
    temp_supplier_dict['suppliedProducts'] = linked_products
    return Supplier(**temp_supplier_dict)

@router.put("/suppliers/{supplier_id}", response_model=Supplier)
async def update_supplier_endpoint(
    supplier_id: int = Path(..., title="The ID of the supplier to update"),
    supplier_in: SupplierCreate = Body(...)
):
    # --- DB Interaction Placeholder ---
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    current_supplier = mock_db_supplier_module["suppliers"][supplier_id]

    if supplier_in.supplierName.lower() != current_supplier.supplierName.lower() and \
        any(s.supplierName.lower() == supplier_in.supplierName.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier name already exists")
    if supplier_in.taxID and supplier_in.taxID != current_supplier.taxID and \
       any(s.taxID and s.taxID.lower() == supplier_in.taxID.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TaxID already exists")
    if supplier_in.email and supplier_in.email != current_supplier.email and \
       any(s.email and s.email.lower() == supplier_in.email.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists")

    updated_supplier_data = supplier_in.model_dump(exclude_unset=True)
    updated_supplier = current_supplier.model_copy(update=updated_supplier_data)
    updated_supplier.updatedAt = datetime.utcnow()
    mock_db_supplier_module["suppliers"][supplier_id] = updated_supplier

    # Populate suppliedProducts for the response
    linked_products = [
        sp for sp in mock_db_supplier_module["supplier_products"].values()
        if sp.supplierID == supplier_id
    ]
    temp_supplier_dict = updated_supplier.model_dump()
    temp_supplier_dict['suppliedProducts'] = linked_products
    return Supplier(**temp_supplier_dict)

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier_endpoint(supplier_id: int = Path(..., title="The ID of the supplier to delete")):
    # --- DB Interaction Placeholder (check for related transactions like POs, invoices) ---
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    # Also delete associated supplier_products links
    ids_to_delete = [sp_id for sp_id, sp in mock_db_supplier_module["supplier_products"].items() if sp.supplierID == supplier_id]
    for sp_id in ids_to_delete:
        del mock_db_supplier_module["supplier_products"][sp_id]

    del mock_db_supplier_module["suppliers"][supplier_id]
    # No return for 204

# --- SupplierProducts Endpoints (Nested under Suppliers) ---

@router.post("/suppliers/{supplier_id}/products", response_model=SupplierProduct, status_code=status.HTTP_201_CREATED)
async def add_product_to_supplier_endpoint(
    supplier_id: int = Path(..., title="The ID of the supplier"),
    supplier_product_in: SupplierProductCreate = Body(...)
):
    # --- DB Interaction Placeholder ---
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    # In a real app, validate productID against the Products table
    # For mock: assume product_id provided in supplier_product_in.productID is valid
    # Check if this product is already linked to this supplier
    if any(sp.supplierID == supplier_id and sp.productID == supplier_product_in.productID
           for sp in mock_db_supplier_module["supplier_products"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This product is already linked to this supplier")

    new_id = mock_db_supplier_module["next_supplier_product_id"]
    db_sp = SupplierProduct(
        supplierProductID=new_id,
        supplierID=supplier_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        **supplier_product_in.model_dump()
    )
    mock_db_supplier_module["supplier_products"][new_id] = db_sp
    mock_db_supplier_module["next_supplier_product_id"] += 1
    return db_sp

@router.get("/suppliers/{supplier_id}/products", response_model=List[SupplierProduct])
async def get_supplier_products_endpoint(supplier_id: int = Path(..., title="The ID of the supplier")):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    linked_products = [
        sp for sp in mock_db_supplier_module["supplier_products"].values()
        if sp.supplierID == supplier_id
    ]
    return linked_products

@router.put("/suppliers/{supplier_id}/products/{product_id}", response_model=SupplierProduct)
async def update_supplier_product_link_endpoint(
    supplier_id: int = Path(..., title="The ID of the supplier"),
    product_id: int = Path(..., title="The ID of the product whose link to update"), # Using actual productID in path
    supplier_product_in: SupplierProductCreate = Body(...) # Input model should not contain productID as it's in path
):
    # --- DB Interaction Placeholder ---
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    # Find the SupplierProduct link
    link_id_to_update = None
    current_link = None
    for sp_id, sp_obj in mock_db_supplier_module["supplier_products"].items():
        if sp_obj.supplierID == supplier_id and sp_obj.productID == product_id:
            link_id_to_update = sp_id
            current_link = sp_obj
            break

    if not current_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product link not found for this supplier")

    # Ensure productID in body matches product_id in path if it were in SupplierProductCreate
    # Since SupplierProductCreate has productID, we should check it
    if supplier_product_in.productID != product_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID in path does not match product ID in body.")

    updated_sp_data = supplier_product_in.model_dump(exclude_unset=True)
    updated_sp = current_link.model_copy(update=updated_sp_data)
    updated_sp.updatedAt = datetime.utcnow()
    mock_db_supplier_module["supplier_products"][link_id_to_update] = updated_sp
    return updated_sp

@router.delete("/suppliers/{supplier_id}/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_from_supplier_endpoint(
    supplier_id: int = Path(..., title="The ID of the supplier"),
    product_id: int = Path(..., title="The ID of the product to unlink") # Using actual productID
):
    # --- DB Interaction Placeholder ---
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")

    link_id_to_delete = None
    for sp_id, sp_obj in mock_db_supplier_module["supplier_products"].items():
        if sp_obj.supplierID == supplier_id and sp_obj.productID == product_id:
            link_id_to_delete = sp_id
            break

    if link_id_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product link not found for this supplier to delete")

    del mock_db_supplier_module["supplier_products"][link_id_to_delete]
    # No return for 204

# Main app for standalone running (for testing this module)
if __name__ == "__main__":
    app_supplier_test = FastAPI(title="ERP Suppliers Module API - Test")
    app_supplier_test.include_router(router)
    import uvicorn
    print("Starting Uvicorn server for Suppliers API (Test)...")
    print("Access OpenAPI docs at http://127.0.0.1:8002/docs") # Use a different port
    uvicorn.run(app_supplier_test, host="127.0.0.1", port=8002, reload=False)
```

**Explanation of `api_supplier_module.py`:**

1.  **`APIRouter`:** A new router for the Suppliers module.
2.  **Pydantic Models:** Imports `Supplier`, `SupplierCreate`, `SupplierProduct`, `SupplierProductCreate` from `models_supplier_module.py`.
3.  **Mock Database (`mock_db_supplier_module`):**
    *   A local mock dictionary for suppliers and their linked products.
4.  **Suppliers Endpoints (CRUD for `/suppliers`):**
    *   `POST /suppliers`: Creates a new supplier. Includes mock checks for unique `supplierName`, `taxID`, and `email`.
    *   `GET /suppliers`: Lists suppliers with basic filtering and pagination. Populates `suppliedProducts` in the response for each supplier.
    *   `GET /suppliers/{supplier_id}`: Retrieves a specific supplier. Populates `suppliedProducts`.
    *   `PUT /suppliers/{supplier_id}`: Updates a supplier. Includes uniqueness checks for relevant fields if changed. Populates `suppliedProducts`.
    *   `DELETE /suppliers/{supplier_id}`: Deletes a supplier and also removes any associated links in `supplier_products` from the mock DB.
5.  **SupplierProducts Endpoints (Nested under `/suppliers/{supplier_id}/products`):**
    *   `POST /suppliers/{supplier_id}/products`: Links an existing product (by `productID` in the request body) to the specified supplier. Includes a check to prevent linking the same product multiple times.
    *   `GET /suppliers/{supplier_id}/products`: Lists all products linked to a specific supplier.
    *   `PUT /suppliers/{supplier_id}/products/{product_id}`: Updates the details of a specific product link for a supplier (e.g., `supplierProductCode`, `defaultLeadTimeDays`). Uses `product_id` from the path to identify the link.
    *   `DELETE /suppliers/{supplier_id}/products/{product_id}`: Removes the link between a supplier and a product.
6.  **Error Handling & Placeholders:** Similar to the other API modules.
7.  **Embedding `SupplierProduct` list:** Supplier responses include the list of products they supply.
8.  **Standalone Test Runner:** Includes an `if __name__ == "__main__":` block to run this module's API independently on a different port (8002) for testing.

This file `api_supplier_module.py` provides the structural API for managing Suppliers and their product links.

This completes the second step of the current plan.
