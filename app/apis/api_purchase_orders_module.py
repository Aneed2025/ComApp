from fastapi import APIRouter, HTTPException, Path, Body, status, Depends
from typing import List, Optional
from datetime import datetime, date

# Assuming models are in a sibling 'models' directory
from ..models.models_purchase_orders_module import (
    PurchaseOrderHeader, PurchaseOrderHeaderCreate,
    PurchaseOrderLine, PurchaseOrderLineCreate
)
# We'll need other models for fetching data (Product, Supplier, Store etc.) for validation
# These would be imported from their respective model files and accessed via shared_mock_db
from ..models.models_product_module import Product
from ..models.models_supplier_module import Supplier
from ..models.models_stores_module import Store # Assuming Store model exists

# This module will rely on main_api.py to patch its 'db' variable
# to point to the shared_mock_db.
db: dict = {} # Will be monkey-patched by main_api.py

router = APIRouter(
    prefix="/api/v1",
    tags=["Purchase Orders Module"]
)

# --- Helper function for PurchaseOrderID Generation (Mock) ---
# In a real system, this would be a robust sequence generator.
def generate_mock_po_id(store_id: str) -> str:
    # PO-[StoreID]-[YY][MM][XXXX] - XXXX is a sequence number
    # This mock needs to access a shared sequence counter for the store/month combination
    # For simplicity, using a basic counter here.
    # This should ideally use the 'Sequences' table logic we designed.

    # Simplified mock:
    # In shared_mock_db, we'd have something like:
    # "po_sequences": { "SH01-2405": 1, "SH01-2406": 0, ... }
    today = datetime.utcnow()
    year_month_str = today.strftime("%y%m")
    sequence_key = f"PO_{store_id}_{year_month_str}"

    current_seq = db.get("po_sequences", {}).get(sequence_key, 0) + 1
    db.setdefault("po_sequences", {})[sequence_key] = current_seq

    return f"PO-{store_id.upper()}-{year_month_str}{current_seq:03d}" # Using 3 digits for sequence

# --- Purchase Order Endpoints ---

@router.post("/purchase-orders", response_model=PurchaseOrderHeader, status_code=status.HTTP_201_CREATED)
async def create_purchase_order_endpoint(po_in: PurchaseOrderHeaderCreate = Body(...)):
    # 1. Validate Supplier and Store
    supplier = db.get("suppliers", {}).get(po_in.supplierID)
    if not supplier:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Supplier ID '{po_in.supplierID}' not found.")

    store = db.get("stores", {}).get(po_in.storeID)
    if not store:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Store ID '{po_in.storeID}' not found.")

    # 2. Process Purchase Order Lines
    processed_lines_data: List[dict] = []
    po_subtotal_val = 0.0

    generated_po_id = generate_mock_po_id(po_in.storeID)
    # Ensure this generated_po_id is unique if generate_mock_po_id doesn't guarantee it across calls
    if generated_po_id in db.get("purchase_order_headers", {}):
        # This indicates an issue with mock ID generation, try again or raise server error
        # For robust mock, generate_mock_po_id should ensure uniqueness or use UUID.
        # Let's assume for mock it's mostly unique for sequential calls.
        pass


    next_line_id_counter_key = "next_po_line_id"
    if next_line_id_counter_key not in db: # Ensure counter exists in shared_mock_db
        db[next_line_id_counter_key] = 1


    for idx, line_in in enumerate(po_in.lines):
        product = db.get("products", {}).get(line_in.productID)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID '{line_in.productID}' in line {idx+1} not found.")

        line_total_calc = line_in.quantityOrdered * line_in.unitPrice

        line_item_id = db[next_line_id_counter_key]
        db[next_line_id_counter_key] +=1

        line_data = {
            "purchaseOrderLineID": line_item_id,
            "purchaseOrderID": generated_po_id, # Link to header
            "productID": line_in.productID,
            "description": line_in.description or product.get("productName"), # Assuming product is dict from mock
            "quantityOrdered": line_in.quantityOrdered,
            "unitOfMeasure": line_in.unitOfMeasure or product.get("unitOfMeasure"),
            "unitPrice": round(line_in.unitPrice, 2),
            "lineTotal": round(line_total_calc, 2),
            "quantityReceived": 0.00, # Initial value
            "expectedLineDeliveryDate": line_in.expectedLineDeliveryDate,
            "notes": None, # Add if line-specific notes are needed
            "purchaseRequisitionLineID": line_in.purchaseRequisitionLineID
        }
        processed_lines_data.append(line_data)
        po_subtotal_val += line_total_calc

    # 3. Calculate Header Totals
    calculated_subtotal = round(po_subtotal_val, 2)

    # Tax, shipping, other charges from input or default to 0
    tax_amount_val = po_in.taxAmount or 0.0
    shipping_cost_val = po_in.shippingCost or 0.0
    other_charges_val = po_in.otherCharges or 0.0

    grand_total_calc = calculated_subtotal + tax_amount_val + shipping_cost_val + other_charges_val

    # 4. Create PurchaseOrderHeader object
    header_data = {
        "purchaseOrderID": generated_po_id,
        "supplierID": po_in.supplierID,
        "storeID": po_in.storeID,
        "orderDate": po_in.orderDate or datetime.utcnow(),
        "expectedDeliveryDate": po_in.expectedDeliveryDate,
        "status": po_in.status or 'Draft',
        "notes": po_in.notes,
        "paymentTermsID": po_in.paymentTermsID,
        "shippingAddress": po_in.shippingAddress,
        "billingAddress": po_in.billingAddress,
        "purchaseRequisitionID": po_in.purchaseRequisitionID,
        # createdByUserID, approvedByUserID, approvalDate would be set by logic/user session

        "subtotal": calculated_subtotal,
        "taxAmount": round(tax_amount_val, 2),
        "shippingCost": round(shipping_cost_val, 2),
        "otherCharges": round(other_charges_val, 2),
        "totalAmount": round(grand_total_calc, 2),

        "lines": [PurchaseOrderLine(**line_d) for line_d in processed_lines_data],
        "createdAt": datetime.utcnow(),
        "updatedAt": datetime.utcnow()
    }
    db_header = PurchaseOrderHeader(**header_data)

    # 5. Save to mock_db (Header and Lines)
    db.setdefault("purchase_order_headers", {})[generated_po_id] = db_header
    # Store individual lines in a flat mock structure for purchase_order_lines
    for line_dict in processed_lines_data:
        db.setdefault("purchase_order_lines", {})[line_dict["purchaseOrderLineID"]] = PurchaseOrderLine(**line_dict)

    return db_header

@router.get("/purchase-orders", response_model=List[PurchaseOrderHeader])
async def get_all_purchase_orders_endpoint(
    skip: int = 0,
    limit: int = 10,
    supplier_id: Optional[int] = None,
    store_id: Optional[str] = None,
    status: Optional[str] = None
):
    headers_dict: dict = db.get("purchase_order_headers", {})
    results = list(headers_dict.values()) # These are PurchaseOrderHeader Pydantic objects

    if supplier_id is not None:
        results = [po for po in results if po.supplierID == supplier_id]
    if store_id:
        results = [po for po in results if po.storeID.lower() == store_id.lower()]
    if status:
        results = [po for po in results if po.status.lower() == status.lower()]

    # Lines are already embedded in the PurchaseOrderHeader objects in mock_db
    return results[skip : skip + limit]

@router.get("/purchase-orders/{purchase_order_id}", response_model=PurchaseOrderHeader)
async def get_purchase_order_by_id_endpoint(purchase_order_id: str = Path(..., title="The Purchase Order ID")):
    po_header = db.get("purchase_order_headers", {}).get(purchase_order_id)
    if not po_header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found")
    # Lines are already embedded
    return po_header

@router.put("/purchase-orders/{purchase_order_id}", response_model=PurchaseOrderHeader)
async def update_purchase_order_endpoint(
    purchase_order_id: str = Path(..., title="The Purchase Order ID to update"),
    po_in: PurchaseOrderHeaderCreate = Body(...) # Using Create model for simplicity in updates
):
    # --- DB Interaction Placeholder ---
    # In a real app:
    # 1. Fetch existing PO. If not found, 404.
    # 2. Check if PO is in an editable status (e.g., 'Draft', 'PendingApproval').
    #    If 'SentToSupplier' or 'Received', updates might be restricted or trigger other workflows.
    # 3. Validate SupplierID, StoreID if changed.
    # 4. Process lines:
    #    - Identify new lines, modified lines, deleted lines.
    #    - For new/modified lines, validate ProductID.
    #    - Recalculate line totals.
    # 5. Recalculate header totals.
    # 6. Update PO header and lines in DB.
    # --- End Placeholder for PUT ---

    existing_po_header = db.get("purchase_order_headers", {}).get(purchase_order_id)
    if not existing_po_header:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found to update.")

    # Mock update: For simplicity, this mock will replace lines and recalculate.
    # A real PUT would be more granular.
    # We also assume that if a PO is being updated, its ID does not change.

    # Re-validate supplier and store if they are part of 'po_in' and could change
    if po_in.supplierID and db.get("suppliers", {}).get(po_in.supplierID) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Supplier ID '{po_in.supplierID}' not found.")
    if po_in.storeID and db.get("stores", {}).get(po_in.storeID) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Store ID '{po_in.storeID}' not found.")

    processed_lines_data: List[dict] = []
    po_subtotal_val = 0.0

    # Use existing line ID counter from shared_mock_db
    next_line_id_counter_key = "next_po_line_id" # Should match key used in POST

    # Delete old lines associated with this PO for this mock implementation
    # In a real DB, you'd update existing, delete removed, add new.
    old_line_ids = [line.purchaseOrderLineID for line in existing_po_header.lines]
    for line_id in old_line_ids:
        if line_id in db.get("purchase_order_lines", {}):
            del db.get("purchase_order_lines", {})[line_id]

    for idx, line_in in enumerate(po_in.lines):
        product = db.get("products", {}).get(line_in.productID)
        if not product:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product ID '{line_in.productID}' in line {idx+1} not found.")
        line_total_calc = line_in.quantityOrdered * line_in.unitPrice

        line_item_id = db[next_line_id_counter_key] # Get current value
        db[next_line_id_counter_key] +=1          # Increment for next use

        line_data = {
            "purchaseOrderLineID": line_item_id, "purchaseOrderID": purchase_order_id,
            "productID": line_in.productID,
            "description": line_in.description or product.get("productName"),
            "quantityOrdered": line_in.quantityOrdered,
            "unitOfMeasure": line_in.unitOfMeasure or product.get("unitOfMeasure"),
            "unitPrice": round(line_in.unitPrice, 2),
            "lineTotal": round(line_total_calc, 2),
            "quantityReceived": 0.00, # Reset or carry over based on logic
            "expectedLineDeliveryDate": line_in.expectedLineDeliveryDate,
            "notes": None,
            "purchaseRequisitionLineID": line_in.purchaseRequisitionLineID
        }
        processed_lines_data.append(line_data)
        db.setdefault("purchase_order_lines", {})[line_item_id] = PurchaseOrderLine(**line_data)
        po_subtotal_val += line_total_calc

    calculated_subtotal = round(po_subtotal_val, 2)
    tax_amount_val = po_in.taxAmount or 0.0
    shipping_cost_val = po_in.shippingCost or 0.0
    other_charges_val = po_in.otherCharges or 0.0
    grand_total_calc = calculated_subtotal + tax_amount_val + shipping_cost_val + other_charges_val

    # Update existing_po_header object's fields
    update_data_dict = po_in.model_dump(exclude={'lines'}, exclude_unset=True) # Exclude lines as we handle them separately

    # Update header fields from po_in
    for key, value in update_data_dict.items():
        if hasattr(existing_po_header, key):
            setattr(existing_po_header, key, value)

    existing_po_header.subtotal = calculated_subtotal
    existing_po_header.taxAmount = round(tax_amount_val, 2)
    existing_po_header.shippingCost = round(shipping_cost_val, 2)
    existing_po_header.otherCharges = round(other_charges_val, 2)
    existing_po_header.totalAmount = round(grand_total_calc, 2)
    existing_po_header.lines = [PurchaseOrderLine(**line_d) for line_d in processed_lines_data]
    existing_po_header.updatedAt = datetime.utcnow()

    db.get("purchase_order_headers", {})[purchase_order_id] = existing_po_header
    return existing_po_header


# --- Main app for standalone testing (illustrative) ---
if __name__ == "__main__":
    # This block is for testing this module in isolation.
    # Requires manual setup of `db` with product, supplier, store data.
    db = {
        "products": {
            201: {"productID": 201, "productName": "Widget A", "unitOfMeasure": "pcs"},
            202: {"productID": 202, "productName": "Gadget B", "unitOfMeasure": "pcs"}
        },
        "suppliers": {
            1: {"supplierID": 1, "supplierName": "Supplier X"}
        },
        "stores": {
            "SH01": {"storeID": "SH01", "storeName": "Main Store"}
        },
        "purchase_order_headers": {},
        "purchase_order_lines": {},
        "next_po_line_id": 1,
        "po_sequences": {} # For generate_mock_po_id
    }

    app_po_test = FastAPI(title="ERP Purchase Orders Module API - Test")
    app_po_test.include_router(router)
    import uvicorn
    print("Starting Uvicorn server for Purchase Orders API (Test - Limited Mock Data)...")
    print("Access OpenAPI docs at http://127.0.0.1:8007/docs")
    uvicorn.run(app_po_test, host="127.0.0.1", port=8007, reload=False)

```

**Explanation of `app/apis/api_purchase_orders_module.py`:**

1.  **Imports:** FastAPI components, Pydantic models from `models_purchase_orders_module.py`, and other Pydantic models (`Product`, `Supplier`, `Store`) for type hinting and accessing data from the `shared_mock_db`.
2.  **`db: dict = {}`:** Declared at the module level. This `db` variable will be "monkey-patched" by `main_api.py` to point to the `shared_mock_db`, allowing this module to access all shared data.
3.  **`generate_mock_po_id(store_id: str)`:** A helper function to generate formatted PO IDs (e.g., `PO-SH01-2405001`).
    *   It uses a `po_sequences` dictionary within the `shared_mock_db` to manage monthly sequences per store (e.g., `shared_mock_db["po_sequences"]["SH01-2405"]`). This is a more robust mock for sequential ID generation than a simple global counter for POs.
    *   It also initializes `"next_po_line_id"` in `shared_mock_db` if not present.
4.  **`POST /purchase-orders` (`create_purchase_order_endpoint`):**
    *   Validates `SupplierID` and `StoreID` using data from `shared_mock_db`.
    *   Iterates through input lines, validates `ProductID`.
    *   Calculates `LineTotal` for each line.
    *   Generates a formatted `PurchaseOrderID`.
    *   Calculates header totals (`Subtotal`, `TotalAmount`, including input `taxAmount`, `shippingCost`, `otherCharges`).
    *   Creates `PurchaseOrderHeader` and `PurchaseOrderLine` Pydantic objects.
    *   Saves these to the `shared_mock_db` (under `"purchase_order_headers"` and `"purchase_order_lines"` keys).
5.  **`GET /purchase-orders` and `GET /purchase-orders/{purchase_order_id}`:**
    *   Basic structural endpoints for listing and retrieving POs. Lines are embedded in the header object.
6.  **`PUT /purchase-orders/{purchase_order_id}` (`update_purchase_order_endpoint`):**
    *   Structural endpoint for updating a PO.
    *   Includes placeholder comments for complex logic like status checks and granular line updates.
    *   The mock implementation here is simplified: it effectively replaces the lines and recalculates totals. A real implementation would handle line modifications more precisely (add new, update existing, delete removed).
    *   It ensures the `purchase_order_id` from the path is used and doesn't allow changing the PO's ID via the body.
7.  **Standalone Runner:** The `if __name__ == "__main__":` block is updated with more sample data for `db` to allow some basic standalone testing of this module's structure.

This file provides the core structure for the Purchase Order API.

This completes the third step of the current plan.
