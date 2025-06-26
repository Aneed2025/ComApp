from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime, date

# Literal type for PO Status
PurchaseOrderStatusLiteral = Literal[
    'Draft', 'PendingApproval', 'Approved', 'SentToSupplier',
    'PartiallyReceived', 'FullyReceived', 'Cancelled', 'Closed'
]

# --- PurchaseOrderLine Models ---

class PurchaseOrderLineBase(BaseModel):
    productID: int
    description: Optional[str] = None # Can be auto-filled from product, but overridable
    quantityOrdered: float = Field(..., gt=0) # gt=0 ensures quantity is positive
    unitOfMeasure: Optional[str] = Field(default=None, max_length=20)
    unitPrice: float = Field(..., ge=0) # Price per unit from supplier

    # lineTotal: float # This will be calculated: quantityOrdered * unitPrice
    expectedLineDeliveryDate: Optional[date] = None
    notes: Optional[str] = None
    purchaseRequisitionLineID: Optional[int] = None # Link to PR line

class PurchaseOrderLineCreate(BaseModel):
    # When creating a PO, frontend sends these for each line
    productID: int
    quantityOrdered: float = Field(..., gt=0)
    unitPrice: float = Field(..., ge=0)
    description: Optional[str] = None
    unitOfMeasure: Optional[str] = Field(default=None, max_length=20)
    expectedLineDeliveryDate: Optional[date] = None
    purchaseRequisitionLineID: Optional[int] = None

class PurchaseOrderLine(PurchaseOrderLineBase):
    purchaseOrderLineID: int # PK from DB
    purchaseOrderID: str     # FK to header
    lineTotal: float = Field(..., ge=0) # Calculated and stored
    quantityReceived: float = Field(default=0.00, ge=0)

    class Config:
        from_attributes = True

# --- PurchaseOrderHeader Models ---

class PurchaseOrderHeaderBase(BaseModel):
    supplierID: int
    storeID: str = Field(..., max_length=10)

    orderDate: datetime
    expectedDeliveryDate: Optional[date] = None
    status: PurchaseOrderStatusLiteral = 'Draft'

    notes: Optional[str] = None
    paymentTermsID: Optional[int] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None

    createdByUserID: Optional[int] = None
    approvedByUserID: Optional[int] = None
    approvalDate: Optional[datetime] = None
    purchaseRequisitionID: Optional[str] = Field(default=None, max_length=50) # Link to PR Header

    # Amounts are typically calculated by the backend based on lines
    subtotal: float = Field(default=0.00, ge=0)
    taxAmount: float = Field(default=0.00, ge=0)
    shippingCost: float = Field(default=0.00, ge=0)
    otherCharges: float = Field(default=0.00, ge=0)
    totalAmount: float = Field(default=0.00, ge=0)

    @validator('orderDate', pre=True, allow_reuse=True)
    def default_order_date_to_now(cls, v):
        return v or datetime.utcnow()

    @validator('expectedDeliveryDate', 'approvalDate', pre=True, allow_reuse=True)
    def parse_optional_dates(cls, v):
        if isinstance(v, str):
            try:
                if 'T' in v or 'Z' in v: # Datetime string
                     return datetime.fromisoformat(v.replace('Z', '+00:00'))
                return datetime.strptime(v, '%Y-%m-%d').date() # Date string
            except ValueError:
                raise ValueError("Invalid date/datetime format. Use ISO format for datetime or YYYY-MM-DD for date.")
        return v # Already a date/datetime object or None


class PurchaseOrderHeaderCreate(BaseModel): # Input model from user/frontend
    supplierID: int
    storeID: str = Field(..., max_length=10)
    orderDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    expectedDeliveryDate: Optional[date] = None
    status: Optional[PurchaseOrderStatusLiteral] = 'Draft'

    notes: Optional[str] = None
    paymentTermsID: Optional[int] = None
    shippingAddress: Optional[str] = None
    billingAddress: Optional[str] = None
    purchaseRequisitionID: Optional[str] = Field(default=None, max_length=50)

    lines: List[PurchaseOrderLineCreate] = Field(..., min_length=1) # Must have at least one line

    # Optional fields that user might set at creation, affecting totals
    # Tax, shipping, other charges might be added by user or calculated later
    taxAmount: Optional[float] = Field(default=0.00, ge=0)
    shippingCost: Optional[float] = Field(default=0.00, ge=0)
    otherCharges: Optional[float] = Field(default=0.00, ge=0)


class PurchaseOrderHeader(PurchaseOrderHeaderBase):
    purchaseOrderID: str # The generated formatted ID
    lines: List[PurchaseOrderLine] = Field(default_factory=list) # Embed full line details in response
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Example Usage
if __name__ == "__main__":
    print("Pydantic Models for Purchase Order Module - Illustrative Examples")

    # PurchaseOrderLineCreate Example
    po_line1_create_data = {"productID": 201, "quantityOrdered": 10, "unitPrice": 25.50}
    po_line1_create = PurchaseOrderLineCreate(**po_line1_create_data)
    print(f"\nPurchaseOrderLineCreate: {po_line1_create.model_dump_json(indent=2)}")

    # PurchaseOrderLine (as if from DB, after backend calculation)
    po_line1_db_data = {
        "purchaseOrderLineID": 1, "purchaseOrderID": "PO-SH01-2405001", "productID": 201,
        "quantityOrdered": 10, "unitPrice": 25.50, "lineTotal": 255.00, "quantityReceived": 0
    }
    po_line1_db = PurchaseOrderLine(**po_line1_db_data)
    print(f"PurchaseOrderLine DB Model: {po_line1_db.model_dump_json(indent=2)}")

    # PurchaseOrderHeaderCreate Example
    po_header_create_data = {
        "supplierID": 1, "storeID": "SH01",
        "lines": [po_line1_create_data, {"productID": 202, "quantityOrdered": 5, "unitPrice": 100.00}],
        "expectedDeliveryDate": "2024-12-15"
    }
    po_header_create = PurchaseOrderHeaderCreate(**po_header_create_data)
    print(f"\nPurchaseOrderHeaderCreate: {po_header_create.model_dump_json(indent=2)}")

    # PurchaseOrderHeader (as if from DB, after backend calculation)
    # Backend would calculate all totals, generate ID, etc.
    po_header_db_data_dict = {
        "purchaseOrderID": "PO-SH01-2405001", "supplierID": 1, "storeID": "SH01",
        "orderDate": datetime.utcnow(), "expectedDeliveryDate": date(2024,12,15),
        "status": "Approved",
        "subtotal": 755.00, # (10 * 25.50) + (5 * 100.00)
        "taxAmount": 75.50, # Example 10% tax
        "totalAmount": 830.50, # 755.00 + 75.50
        "lines": [po_line1_db.model_dump()], # Simplified, would have line2 as well
        "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
    }
    # Convert lines back to PurchaseOrderLine objects
    po_header_db_data_dict["lines"] = [PurchaseOrderLine(**line_data) for line_data in po_header_db_data_dict["lines"]]

    po_header_db = PurchaseOrderHeader(**po_header_db_data_dict)
    print(f"PurchaseOrderHeader DB Model: {po_header_db.model_dump_json(indent=2)}")

    try:
        PurchaseOrderLineCreate(productID=1, quantityOrdered=0, unitPrice=10) # Zero quantity
    except ValueError as e:
        print(f"\nPurchaseOrderLineCreate Error: {e}")

```

**Explanation of `app/models/models_purchase_orders_module.py`:**

1.  **`PurchaseOrderStatusLiteral`**: Defines allowed string values for PO status.
2.  **`PurchaseOrderLineBase`**: Common fields for a PO line. `lineTotal` is commented out as it's always calculated.
3.  **`PurchaseOrderLineCreate`**: Represents what the client sends to create a new PO line. It focuses on essential inputs: `productID`, `quantityOrdered`, `unitPrice`, and optional descriptive/reference fields.
4.  **`PurchaseOrderLine`**: Full representation of a PO line, including the database-generated `purchaseOrderLineID`, the calculated `lineTotal`, and `quantityReceived` (which will be updated by GRN process).
5.  **`PurchaseOrderHeaderBase`**: Common fields for a PO header. Many amount fields default to 0 as they are calculated by the backend. Includes validators for date fields.
6.  **`PurchaseOrderHeaderCreate`**: Data needed to initiate PO creation.
    *   Includes essential header info (`supplierID`, `storeID`).
    *   Takes `lines: List[PurchaseOrderLineCreate]`.
    *   Allows optional input for fields like `taxAmount`, `shippingCost`, `otherCharges` if they are known at creation and not purely calculated.
7.  **`PurchaseOrderHeader`**: Full representation of a PO header.
    *   Includes the generated `purchaseOrderID`.
    *   Embeds `lines: List[PurchaseOrderLine]` for comprehensive API responses.
8.  **Validators**:
    *   `default_order_date_to_now` in `PurchaseOrderHeaderBase` ensures `orderDate` defaults to now if not provided.
    *   `parse_optional_dates` handles string-to-date/datetime conversion for optional date fields.
    *   Pydantic `Field` used for basic validation (e.g., `gt=0` for quantities, `ge=0` for prices/amounts).
9.  **`Config: from_attributes = True`**: For Pydantic models.
10. **Illustrative Examples**: The `if __name__ == "__main__":` block shows model usage.

This file provides the Pydantic data models for the Purchase Order module, distinguishing between creation payloads and full entity representations with backend-calculated fields.

This completes the second step of the current plan.
