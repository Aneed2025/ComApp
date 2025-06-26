from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, date

# --- GoodsReceiptNoteLine Models ---

class GoodsReceiptNoteLineBase(BaseModel):
    productID: int = Field(..., description="Identifier of the product being received.")
    purchaseOrderLineID: Optional[int] = Field(default=None, description="Link to the specific PO line, if applicable.")

    quantityOrdered: Optional[float] = Field(default=None, ge=0, description="Quantity originally ordered on the PO line, for reference.")
    quantityReceived: float = Field(..., gt=0, description="Quantity of the product actually received.")

    unitPriceAtReceipt: Optional[float] = Field(default=None, ge=0, description="Cost price of the product at the time of receipt. May differ from PO price.")

    batchNumber: Optional[str] = Field(default=None, max_length=50, description="Batch or lot number if the product is batch-tracked.")
    expiryDate: Optional[date] = Field(default=None, description="Expiry date if the product has one.")

    notes: Optional[str] = Field(default=None, description="Notes specific to this received line item.")

class GoodsReceiptNoteLineCreate(GoodsReceiptNoteLineBase):
    pass

class GoodsReceiptNoteLine(GoodsReceiptNoteLineBase):
    grnLineID: int = Field(..., description="Unique identifier for the GRN line item.")
    grnHeaderID: str = Field(..., description="Identifier of the GRN header this line belongs to.") # Using str to match GRNHeader.grnID
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# --- GoodsReceiptNoteHeader Models ---

class GoodsReceiptNoteHeaderBase(BaseModel):
    purchaseOrderID: Optional[str] = Field(default=None, description="Identifier of the Purchase Order this GRN is for, if applicable.")
    supplierID: Optional[int] = Field(default=None, description="Identifier of the supplier providing the goods.")
    storeID: str = Field(..., description="Identifier of the store/warehouse receiving the goods.") # Changed to str to match Stores.StoreID

    receiptDate: date = Field(default_factory=date.today, description="Date when the goods were received.")
    supplierInvoiceNo: Optional[str] = Field(default=None, max_length=50, description="Supplier's invoice number accompanying the shipment.")
    receivedByUserID: Optional[int] = Field(default=None, description="Identifier of the user who recorded the receipt.") # Assuming an Employees/Users table

    status: str = Field(default="Draft", max_length=20, description="Status of the GRN (e.g., Draft, Posted, Cancelled).")
    notes: Optional[str] = Field(default=None, description="General notes for the GRN.")

class GoodsReceiptNoteHeaderCreate(GoodsReceiptNoteHeaderBase):
    lines: List[GoodsReceiptNoteLineCreate] = Field(..., description="List of line items received.")

class GoodsReceiptNoteHeader(GoodsReceiptNoteHeaderBase):
    grnID: str = Field(..., description="Unique identifier for the GRN, formatted (e.g., GRN-[StoreID]-[YY][MM][XXXX]).")
    createdAt: datetime
    updatedAt: datetime
    lines: List[GoodsReceiptNoteLine] = Field(default_factory=list, description="List of line items received.")

    class Config:
        from_attributes = True

# Illustrative examples (mainly for documentation or testing)
if __name__ == "__main__":
    # Example GRN Line Create
    grn_line_create_example = GoodsReceiptNoteLineCreate(
        productID=101,
        purchaseOrderLineID=1,
        quantityOrdered=10,
        quantityReceived=8,
        unitPriceAtReceipt=15.50,
        batchNumber="BATCH007",
        expiryDate=date(2025, 12, 31)
    )
    print("GRN Line Create Example:", grn_line_create_example.model_dump_json(indent=2))

    # Example GRN Header Create
    grn_header_create_example = GoodsReceiptNoteHeaderCreate(
        purchaseOrderID="PO-SH01-2405001",
        supplierID=201,
        storeID="SH01",
        receiptDate=date.today(),
        supplierInvoiceNo="SUPINV-9876",
        receivedByUserID=301,
        status="Draft",
        lines=[grn_line_create_example]
    )
    print("\nGRN Header Create Example:", grn_header_create_example.model_dump_json(indent=2))

    # Example GRN Header (as stored/retrieved)
    grn_header_example = GoodsReceiptNoteHeader(
        grnID="GRN-SH01-2407001",
        purchaseOrderID="PO-SH01-2405001",
        supplierID=201,
        storeID="SH01",
        receiptDate=date.today(),
        supplierInvoiceNo="SUPINV-9876",
        receivedByUserID=301,
        status="Posted",
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        lines=[
            GoodsReceiptNoteLine(
                grnLineID=1,
                grnHeaderID="GRN-SH01-2407001",
                productID=101,
                purchaseOrderLineID=1,
                quantityOrdered=10,
                quantityReceived=8,
                unitPriceAtReceipt=15.50,
                batchNumber="BATCH007",
                expiryDate=date(2025, 12, 31),
                createdAt=datetime.utcnow(),
                updatedAt=datetime.utcnow()
            )
        ]
    )
    print("\nGRN Header Example:", grn_header_example.model_dump_json(indent=2))
