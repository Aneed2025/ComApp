from fastapi import FastAPI, HTTPException, APIRouter, Path, Body, status
from typing import List, Optional
from datetime import datetime

# Assuming models_customer_module.py is in a directory accessible by PYTHONPATH
# Adjust import path based on your project structure, e.g., from ..models.models_customer_module import ...
from models_customer_module import (
    CustomerGroup, CustomerGroupCreate,
    Customer, CustomerCreate
)

# Mock Database
# IMPORTANT: When integrated into main_api.py, this local mock_db will be
# superseded by the shared_mock_db instance from main_api.py.
mock_db_customer_module = {
    "customer_groups": {
        1: CustomerGroup(customerGroupID=1, groupName="Default Retail", description="Default retail customer group", createdAt=datetime.utcnow(),updatedAt=datetime.utcnow())
    },
    "customers": {},
    "next_customer_group_id": 2,
    "next_customer_id": 1,
}

router = APIRouter(
    prefix="/api/v1",
    tags=["Customers Module"]
)

# --- CustomerGroups Endpoints ---
@router.post("/customer-groups", response_model=CustomerGroup, status_code=status.HTTP_201_CREATED)
async def create_customer_group_endpoint(customer_group_in: CustomerGroupCreate):
    if any(cg.groupName.lower() == customer_group_in.groupName.lower() for cg in mock_db_customer_module["customer_groups"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CustomerGroup name already exists")
    new_id = mock_db_customer_module["next_customer_group_id"]
    db_cg = CustomerGroup(
        customerGroupID=new_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        **customer_group_in.model_dump()
    )
    mock_db_customer_module["customer_groups"][new_id] = db_cg
    mock_db_customer_module["next_customer_group_id"] += 1
    return db_cg

@router.get("/customer-groups", response_model=List[CustomerGroup])
async def get_all_customer_groups_endpoint(skip: int = 0, limit: int = 100):
    groups_list = list(mock_db_customer_module["customer_groups"].values())
    return groups_list[skip : skip + limit]

@router.get("/customer-groups/{group_id}", response_model=CustomerGroup)
async def get_customer_group_by_id_endpoint(group_id: int = Path(..., title="The ID of the customer group")):
    cg = mock_db_customer_module["customer_groups"].get(group_id)
    if not cg: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CustomerGroup not found")
    return cg

@router.put("/customer-groups/{group_id}", response_model=CustomerGroup)
async def update_customer_group_endpoint(
    group_id: int = Path(..., title="The ID of the customer group to update"),
    customer_group_in: CustomerGroupCreate = Body(...)
):
    if group_id not in mock_db_customer_module["customer_groups"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CustomerGroup not found")
    current_cg = mock_db_customer_module["customer_groups"][group_id]
    if customer_group_in.groupName.lower() != current_cg.groupName.lower() and \
       any(cg.groupName.lower() == customer_group_in.groupName.lower() for cg_id, cg in mock_db_customer_module["customer_groups"].items() if cg_id != group_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="CustomerGroup name already exists")
    updated_cg_data = customer_group_in.model_dump(exclude_unset=True)
    updated_cg = current_cg.model_copy(update=updated_cg_data)
    updated_cg.updatedAt = datetime.utcnow()
    mock_db_customer_module["customer_groups"][group_id] = updated_cg
    return updated_cg

@router.delete("/customer-groups/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_group_endpoint(group_id: int = Path(..., title="The ID of the customer group to delete")):
    if group_id not in mock_db_customer_module["customer_groups"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CustomerGroup not found")
    if any(cust.customerGroupID == group_id for cust in mock_db_customer_module["customers"].values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="CustomerGroup is in use by customers.")
    del mock_db_customer_module["customer_groups"][group_id]

# --- Customers Endpoints ---
@router.post("/customers", response_model=Customer, status_code=status.HTTP_201_CREATED)
async def create_customer_endpoint(customer_in: CustomerCreate):
    if customer_in.nationalID and \
       any(c.nationalID and c.nationalID.lower() == customer_in.nationalID.lower() for c in mock_db_customer_module["customers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NationalID already exists.")
    if customer_in.email and \
       any(c.email and c.email.lower() == customer_in.email.lower() for c in mock_db_customer_module["customers"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    if customer_in.customerGroupID and customer_in.customerGroupID not in mock_db_customer_module["customer_groups"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CustomerGroupID '{customer_in.customerGroupID}' not found.")
    new_id = mock_db_customer_module["next_customer_id"]
    db_customer = Customer(customerID=new_id, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow(), customerGroup=None, **customer_in.model_dump())
    mock_db_customer_module["customers"][new_id] = db_customer
    mock_db_customer_module["next_customer_id"] += 1
    if db_customer.customerGroupID: db_customer.customerGroup = mock_db_customer_module["customer_groups"].get(db_customer.customerGroupID)
    return db_customer

@router.get("/customers", response_model=List[Customer])
async def get_all_customers_endpoint(skip: int = 0, limit: int = 10, customer_group_id: Optional[int] = None, name: Optional[str] = None, national_id: Optional[str] = None, email: Optional[str] = None):
    results = list(mock_db_customer_module["customers"].values())
    if customer_group_id is not None: results = [c for c in results if c.customerGroupID == customer_group_id]
    if name: results = [c for c in results if name.lower() in c.customerName.lower()]
    if national_id: results = [c for c in results if c.nationalID and national_id.lower() == c.nationalID.lower()]
    if email: results = [c for c in results if c.email and email.lower() == c.email.lower()]
    response_list = []
    for cust_data in results[skip : skip + limit]:
        group_obj = None
        if cust_data.customerGroupID: group_obj = mock_db_customer_module["customer_groups"].get(cust_data.customerGroupID)
        temp_cust_dict = cust_data.model_dump(); temp_cust_dict['customerGroup'] = group_obj
        response_list.append(Customer(**temp_cust_dict))
    return response_list

@router.get("/customers/{customer_id}", response_model=Customer)
async def get_customer_by_id_endpoint(customer_id: int = Path(..., title="The ID of the customer")):
    cust = mock_db_customer_module["customers"].get(customer_id)
    if not cust: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    group_obj = None
    if cust.customerGroupID: group_obj = mock_db_customer_module["customer_groups"].get(cust.customerGroupID)
    temp_cust_dict = cust.model_dump(); temp_cust_dict['customerGroup'] = group_obj
    return Customer(**temp_cust_dict)

@router.put("/customers/{customer_id}", response_model=Customer)
async def update_customer_endpoint(customer_id: int = Path(..., title="The ID of the customer"), customer_in: CustomerCreate = Body(...)):
    if customer_id not in mock_db_customer_module["customers"]: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    current_customer = mock_db_customer_module["customers"][customer_id]
    if customer_in.nationalID and customer_in.nationalID != current_customer.nationalID and \
       any(c.nationalID and c.nationalID.lower() == customer_in.nationalID.lower() for cid, c in mock_db_customer_module["customers"].items() if cid != customer_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="NationalID already exists.")
    if customer_in.email and customer_in.email != current_customer.email and \
       any(c.email and c.email.lower() == customer_in.email.lower() for cid, c in mock_db_customer_module["customers"].items() if cid != customer_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists.")
    if customer_in.customerGroupID and customer_in.customerGroupID not in mock_db_customer_module["customer_groups"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CustomerGroupID '{customer_in.customerGroupID}' not found.")
    updated_customer_data = customer_in.model_dump(exclude_unset=True)
    updated_customer = current_customer.model_copy(update=updated_customer_data)
    updated_customer.updatedAt = datetime.utcnow()
    mock_db_customer_module["customers"][customer_id] = updated_customer
    group_obj = None
    if updated_customer.customerGroupID: group_obj = mock_db_customer_module["customer_groups"].get(updated_customer.customerGroupID)
    temp_cust_dict = updated_customer.model_dump(); temp_cust_dict['customerGroup'] = group_obj
    return Customer(**temp_cust_dict)

@router.delete("/customers/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer_endpoint(customer_id: int = Path(..., title="The ID of the customer")):
    if customer_id not in mock_db_customer_module["customers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found")
    # Placeholder for checking transactions
    del mock_db_customer_module["customers"][customer_id]

# Standalone runner for testing
if __name__ == "__main__":
    app_test = FastAPI(title="Customers API Test")
    app_test.include_router(router)
    import uvicorn
    uvicorn.run(app_test, host="127.0.0.1", port=8001)
```
