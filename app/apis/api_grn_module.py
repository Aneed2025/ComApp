from fastapi import APIRouter, HTTPException, Path, Body, status
from typing import List, Optional
from datetime import datetime, date

# Assuming models_grn_module.py is in app/models/
from ..models.models_grn_module import (
    GoodsReceiptNoteHeader, GoodsReceiptNoteHeaderCreate,
    GoodsReceiptNoteLine, GoodsReceiptNoteLineCreate
)
# For accessing other modules' data (e.g., Products, Stores, Suppliers, PurchaseOrders) from shared_mock_db
# This db object will be patched by main_api.py to point to shared_mock_db
db = {
    "goods_receipt_note_headers": {},
    "goods_receipt_note_lines": {},
    "next_grn_header_id_counter": {}, # Keyed by storeID for GRN-StoreID-YYMMXXXX format
    "next_grn_line_id": 1,
    # Other necessary data stores will be in shared_mock_db accessed via this 'db' object
    # e.g., db["products"], db["stores"], db["suppliers"], db["purchase_order_headers"]
}

router = APIRouter(
    prefix="/api/v1/grns",
    tags=["Goods Receipt Notes (GRN) Module"]
)

def get_next_grn_id_for_store(store_id: str) -> str:
    """
    Generates a formatted GRN ID: GRN-[StoreID]-[YY][MM][XXXX]
    This is a simplified mock version. A real implementation would need
    robust sequence generation, potentially from a database sequence or
    a dedicated sequence table that resets monthly or yearly per store.
    """
    today = date.today()
    year_month = today.strftime("%y%m") # YYMM format

    # Initialize counter for the store and year_month if not present
    if store_id not in db["next_grn_header_id_counter"]:
        db["next_grn_header_id_counter"][store_id] = {}
    if year_month not in db["next_grn_header_id_counter"][store_id]:
        db["next_grn_header_id_counter"][store_id][year_month] = 1

    seq_num = db["next_grn_header_id_counter"][store_id][year_month]
    db["next_grn_header_id_counter"][store_id][year_month] += 1

    return f"GRN-{store_id}-{year_month}{seq_num:04d}"


@router.post("", response_model=GoodsReceiptNoteHeader, status_code=status.HTTP_201_CREATED)
async def create_grn_endpoint(grn_in: GoodsReceiptNoteHeaderCreate = Body(...)):
    # --- Mock Validations (In a real app, these would involve DB queries) ---
    if not db.get("stores") or grn_in.storeID not in db["stores"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"StoreID '{grn_in.storeID}' not found.")

    if grn_in.supplierID and (not db.get("suppliers") or grn_in.supplierID not in db["suppliers"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SupplierID '{grn_in.supplierID}' not found.")

    if grn_in.purchaseOrderID and (not db.get("purchase_order_headers") or grn_in.purchaseOrderID not in db["purchase_order_headers"]):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"PurchaseOrderID '{grn_in.purchaseOrderID}' not found.")

    # Validate products in lines
    for line in grn_in.lines:
        if not db.get("products") or line.productID not in db["products"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"ProductID '{line.productID}' in lines not found.")
        product = db["products"][line.productID]
        if product.requiresExpiryDate and not line.expiryDate:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product '{product.productName}' requires an expiry date.")
        if product.requiresBatchNumber and not line.batchNumber:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Product '{product.productName}' requires a batch number.")

    # --- Create GRN Header ---
    generated_grn_id = get_next_grn_id_for_store(grn_in.storeID)
    if generated_grn_id in db["goods_receipt_note_headers"]:
         # Fallback for extremely rare collision in mock, or if sequence logic needs improvement
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="GRN ID collision, try again.")

    db_grn_header = GoodsReceiptNoteHeader(
        grnID=generated_grn_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        lines=[], # Lines will be added separately
        **grn_in.model_dump(exclude={"lines"}) # Exclude lines from header base creation
    )

    # --- Create GRN Lines ---
    created_lines: List[GoodsReceiptNoteLine] = []
    for line_in in grn_in.lines:
        line_id = db["next_grn_line_id"]
        db_line = GoodsReceiptNoteLine(
            grnLineID=line_id,
            grnHeaderID=db_grn_header.grnID,
            createdAt=datetime.utcnow(),
            updatedAt=datetime.utcnow(),
            **line_in.model_dump()
        )
        db["goods_receipt_note_lines"][line_id] = db_line
        created_lines.append(db_line)
        db["next_grn_line_id"] += 1

    db_grn_header.lines = created_lines
    db["goods_receipt_note_headers"][db_grn_header.grnID] = db_grn_header

    # --- Mock Inventory Update (Placeholder) ---
    # In a real system, this is where you would iterate through `created_lines`
    # and update detailed inventory (e.g., ProductStockBatches)
    # For example:
    # for line in created_lines:
    #   update_inventory(store_id=db_grn_header.storeID, product_id=line.productID,
    #                    quantity_change=line.quantityReceived, batch_number=line.batchNumber,
    #                    expiry_date=line.expiryDate, cost_price=line.unitPriceAtReceipt)
    #   update_product_last_purchase_price(product_id=line.productID, price=line.unitPriceAtReceipt)
    #   if line.purchaseOrderLineID:
    #       update_po_line_received_quantity(line.purchaseOrderLineID, line.quantityReceived)

    print(f"Mock GRN created: {db_grn_header.grnID}. Inventory update would occur here.")

    return db_grn_header

@router.get("", response_model=List[GoodsReceiptNoteHeader])
async def get_all_grns_endpoint(
    skip: int = 0,
    limit: int = 10,
    store_id: Optional[str] = None,
    supplier_id: Optional[int] = None,
    purchase_order_id: Optional[str] = None,
    status: Optional[str] = None
):
    results = list(db["goods_receipt_note_headers"].values())

    # Filtering (mock implementation)
    if store_id: results = [g for g in results if g.storeID == store_id]
    if supplier_id: results = [g for g in results if g.supplierID == supplier_id]
    if purchase_order_id: results = [g for g in results if g.purchaseOrderID == purchase_order_id]
    if status: results = [g for g in results if g.status.lower() == status.lower()]

    return results[skip : skip + limit]

@router.get("/{grn_id}", response_model=GoodsReceiptNoteHeader)
async def get_grn_by_id_endpoint(grn_id: str = Path(..., description="The formatted ID of the GRN to retrieve (e.g., GRN-SH01-24070001)")):
    grn = db["goods_receipt_note_headers"].get(grn_id)
    if not grn:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GRN not found")
    return grn

@router.put("/{grn_id}", response_model=GoodsReceiptNoteHeader)
async def update_grn_endpoint(
    grn_id: str = Path(..., description="The ID of the GRN to update"),
    grn_update_data: GoodsReceiptNoteHeaderCreate = Body(...) # Using Create model for simplicity, can be a dedicated Update model
):
    """
    Structural endpoint for updating a GRN.
    In a real system, updating a posted GRN might be restricted or require specific logic.
    This mock allows updating fields but doesn't re-process lines or inventory for simplicity.
    Line item updates would typically be handled via separate endpoints or more complex logic.
    """
    if grn_id not in db["goods_receipt_note_headers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GRN not found")

    current_grn = db["goods_receipt_note_headers"][grn_id]
    if current_grn.status.lower() == "posted" and grn_update_data.status.lower() != "posted":
         print(f"Warning: Attempting to change status of already posted GRN {grn_id}")
         # In a real app, this might be disallowed or trigger complex reversal logic.

    # Basic update of header fields (excluding lines for this mock)
    update_data_dict = grn_update_data.model_dump(exclude_unset=True, exclude={"lines"})
    updated_grn_header = current_grn.model_copy(update=update_data_dict)
    updated_grn_header.updatedAt = datetime.utcnow()

    # For this mock, we are not re-processing lines.
    # A full update might involve deleting old lines and creating new ones, or updating existing ones.
    # We will retain the original lines for this structural example.
    updated_grn_header.lines = current_grn.lines

    db["goods_receipt_note_headers"][grn_id] = updated_grn_header
    return updated_grn_header

# Placeholder for deleting a GRN - complex due to inventory implications
@router.delete("/{grn_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_grn_endpoint(grn_id: str = Path(..., description="The ID of the GRN to delete")):
    """
    Structural endpoint for deleting a GRN.
    In a real system, deleting a GRN that has been posted to inventory is highly problematic
    and would require reversal of inventory transactions. Usually, GRNs are cancelled or adjusted.
    This mock simply removes it from the dictionary.
    """
    if grn_id not in db["goods_receipt_note_headers"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="GRN not found")

    # Delete associated lines first (mock)
    lines_to_delete = [line_id for line_id, line in db["goods_receipt_note_lines"].items() if line.grnHeaderID == grn_id]
    for line_id in lines_to_delete:
        del db["goods_receipt_note_lines"][line_id]

    del db["goods_receipt_note_headers"][grn_id]
    print(f"Mock GRN {grn_id} and its lines deleted. Inventory reversal would be needed in a real system.")
    return

# Further considerations for a real implementation:
# - Endpoint to "Post" a GRN: Changes status and triggers inventory updates.
# - More granular line item management (add/update/delete lines on an existing GRN if status allows).
# - Handling of stock shortages/over-receipts against PO.
# - Integration with a proper database and transaction management.
# - Robust error handling and logging.
# - User permissions for GRN operations.
# - Linking to financial processes (e.g., creating a Purchase Invoice based on GRN).
# - Reporting (e.g., GRNs pending invoicing, received items by supplier/product).
# - Barcode scanning support for product identification during receipt.
# - Support for returns to supplier (which might generate a negative GRN or a separate document type).
# - Audit trail for all GRN changes.
# - Handling of different product types (serialized, non-serialized, service items if applicable).
# - Integration with quality control processes if goods need inspection before acceptance.
# - Landed cost calculations.
# - Printing GRN documents.
# - Notifications (e.g., to purchasing department when goods are received).
# - Handling of partial deliveries and backorders more explicitly.
# - Direct GRN (without PO) needs careful consideration for costing and supplier assignment.
# - Three-way matching (PO-GRN-Invoice).
```
