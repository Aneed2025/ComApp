from fastapi import FastAPI, HTTPException, APIRouter, Path, Body, status
from typing import List, Optional
from datetime import datetime

# Assuming models_supplier_module.py is in a directory accessible by PYTHONPATH
# For the structure app/models/ and app/apis/, with main_api.py in app/:
from ..models.models_supplier_module import (
    Supplier, SupplierCreate,
    SupplierProduct, SupplierProductCreate
)

# Mock Database
# IMPORTANT: When integrated into main_api.py, this local mock_db will be
# superseded by the shared_mock_db instance from main_api.py.
mock_db_supplier_module = { 
    "suppliers": {},
    "supplier_products": {}, 
    "next_supplier_id": 1,
    "next_supplier_product_id": 1,
}

router = APIRouter(
    prefix="/api/v1", 
    tags=["Suppliers Module"]
)

# --- Suppliers Endpoints ---
@router.post("/suppliers", response_model=Supplier, status_code=status.HTTP_201_CREATED)
async def create_supplier_endpoint(supplier_in: SupplierCreate):
    if any(s.supplierName.lower() == supplier_in.supplierName.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier name already exists")
    if supplier_in.taxID and \
       any(s.taxID and s.taxID.lower() == supplier_in.taxID.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TaxID already exists.")
    if supplier_in.email and \
       any(s.email and s.email.lower() == supplier_in.email.lower() for s in mock_db_supplier_module["suppliers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")

    new_id = mock_db_supplier_module["next_supplier_id"]
    db_supplier = Supplier(
        supplierID=new_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        suppliedProducts=[], 
        **supplier_in.model_dump()
    )
    mock_db_supplier_module["suppliers"][new_id] = db_supplier
    mock_db_supplier_module["next_supplier_id"] += 1
    return db_supplier

@router.get("/suppliers", response_model=List[Supplier])
async def get_all_suppliers_endpoint(skip: int = 0, limit: int = 10, name: Optional[str] = None, tax_id: Optional[str] = None, email: Optional[str] = None):
    results = list(mock_db_supplier_module["suppliers"].values())
    if name: results = [s for s in results if name.lower() in s.supplierName.lower()]
    if tax_id: results = [s for s in results if s.taxID and tax_id.lower() == s.taxID.lower()]
    if email: results = [s for s in results if s.email and email.lower() == s.email.lower()]
    response_list = []
    for supplier_data in results[skip : skip + limit]:
        linked_products = [sp for sp in mock_db_supplier_module["supplier_products"].values() if sp.supplierID == supplier_data.supplierID]
        temp_supplier_dict = supplier_data.model_dump(); temp_supplier_dict['suppliedProducts'] = linked_products
        response_list.append(Supplier(**temp_supplier_dict))
    return response_list

@router.get("/suppliers/{supplier_id}", response_model=Supplier)
async def get_supplier_by_id_endpoint(supplier_id: int = Path(..., title="The ID of the supplier")):
    supplier = mock_db_supplier_module["suppliers"].get(supplier_id)
    if not supplier: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    linked_products = [sp for sp in mock_db_supplier_module["supplier_products"].values() if sp.supplierID == supplier_id]
    temp_supplier_dict = supplier.model_dump(); temp_supplier_dict['suppliedProducts'] = linked_products
    return Supplier(**temp_supplier_dict)

@router.put("/suppliers/{supplier_id}", response_model=Supplier)
async def update_supplier_endpoint(supplier_id: int = Path(..., title="The ID of the supplier"), supplier_in: SupplierCreate = Body(...)):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    current_supplier = mock_db_supplier_module["suppliers"][supplier_id]
    if supplier_in.supplierName.lower() != current_supplier.supplierName.lower() and \
        any(s.supplierName.lower() == supplier_in.supplierName.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Supplier name already exists")
    if supplier_in.taxID and supplier_in.taxID != current_supplier.taxID and \
       any(s.taxID and s.taxID.lower() == supplier_in.taxID.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="TaxID already exists.")
    if supplier_in.email and supplier_in.email != current_supplier.email and \
       any(s.email and s.email.lower() == supplier_in.email.lower() for s_id, s in mock_db_supplier_module["suppliers"].items() if s_id != supplier_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    updated_supplier_data = supplier_in.model_dump(exclude_unset=True)
    updated_supplier = current_supplier.model_copy(update=updated_supplier_data)
    updated_supplier.updatedAt = datetime.utcnow()
    mock_db_supplier_module["suppliers"][supplier_id] = updated_supplier
    linked_products = [sp for sp in mock_db_supplier_module["supplier_products"].values() if sp.supplierID == supplier_id]
    temp_supplier_dict = updated_supplier.model_dump(); temp_supplier_dict['suppliedProducts'] = linked_products
    return Supplier(**temp_supplier_dict)

@router.delete("/suppliers/{supplier_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_supplier_endpoint(supplier_id: int = Path(..., title="The ID of the supplier")):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    ids_to_delete = [sp_id for sp_id, sp in mock_db_supplier_module["supplier_products"].items() if sp.supplierID == supplier_id]
    for sp_id in ids_to_delete: del mock_db_supplier_module["supplier_products"][sp_id]
    del mock_db_supplier_module["suppliers"][supplier_id]

# --- SupplierProducts Endpoints (Nested under Suppliers) ---
@router.post("/suppliers/{supplier_id}/products", response_model=SupplierProduct, status_code=status.HTTP_201_CREATED)
async def add_product_to_supplier_endpoint(supplier_id: int = Path(..., title="Supplier ID"), supplier_product_in: SupplierProductCreate = Body(...)):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    # In a real app, validate productID against Products table via shared_mock_db
    if any(sp.supplierID == supplier_id and sp.productID == supplier_product_in.productID for sp in mock_db_supplier_module["supplier_products"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product already linked to supplier.")
    new_id = mock_db_supplier_module["next_supplier_product_id"]
    db_sp = SupplierProduct(supplierProductID=new_id, supplierID=supplier_id, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow(), **supplier_product_in.model_dump())
    mock_db_supplier_module["supplier_products"][new_id] = db_sp
    mock_db_supplier_module["next_supplier_product_id"] += 1
    return db_sp

@router.get("/suppliers/{supplier_id}/products", response_model=List[SupplierProduct])
async def get_supplier_products_endpoint(supplier_id: int = Path(..., title="Supplier ID")):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    return [sp for sp in mock_db_supplier_module["supplier_products"].values() if sp.supplierID == supplier_id]

@router.put("/suppliers/{supplier_id}/products/{product_id_in_path}", response_model=SupplierProduct)
async def update_supplier_product_link_endpoint(supplier_id: int = Path(..., title="Supplier ID"), product_id_in_path: int = Path(..., title="Product ID"), supplier_product_in: SupplierProductCreate = Body(...)):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    if supplier_product_in.productID != product_id_in_path:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Product ID in path mismatch body.")
    link_to_update = next((sp for sp_id, sp in mock_db_supplier_module["supplier_products"].items() if sp.supplierID == supplier_id and sp.productID == product_id_in_path), None)
    if not link_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product link not found.")
    updated_sp_data = supplier_product_in.model_dump(exclude_unset=True)
    updated_sp_data['productID'] = product_id_in_path 
    updated_sp = link_to_update.model_copy(update=updated_sp_data)
    updated_sp.updatedAt = datetime.utcnow()
    mock_db_supplier_module["supplier_products"][link_to_update.supplierProductID] = updated_sp 
    return updated_sp

@router.delete("/suppliers/{supplier_id}/products/{product_id_in_path}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_product_from_supplier_endpoint(supplier_id: int = Path(..., title="Supplier ID"), product_id_in_path: int = Path(..., title="Product ID")):
    if supplier_id not in mock_db_supplier_module["suppliers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Supplier not found")
    link_id_to_delete = next((sp_id for sp_id, sp in mock_db_supplier_module["supplier_products"].items() if sp.supplierID == supplier_id and sp.productID == product_id_in_path), None)
    if link_id_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product link not found.")
    del mock_db_supplier_module["supplier_products"][link_id_to_delete]
