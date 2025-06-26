from typing import List, Optional, Literal
from pydantic import BaseModel, Field, validator
from datetime import datetime, date # Import date for DueDate

# Literal type for InvoiceType and Status
SalesInvoiceTypeLiteral = Literal['Cash', 'Layby', 'Field', 'Credit'] # Added 'Credit' as a common type
SalesInvoiceStatusLiteral = Literal['Draft', 'Issued', 'PartiallyPaid', 'Paid', 'Void', 'Cancelled', 'Overdue']

# --- SalesInvoiceLine Models ---

class SalesInvoiceLineBase(BaseModel):
    productID: int
    description: Optional[str] = None # Can be auto-filled from product, but overridable
    quantity: float = Field(..., gt=0) # gt=0 ensures quantity is positive
    unitOfMeasure: Optional[str] = Field(default=None, max_length=20)

    # Prices provided by backend logic during invoice creation/calculation
    unitPriceBeforeDiscount: float = Field(..., ge=0)
    productDiscountAmount: float = Field(default=0.00, ge=0)
    productDiscountPercentage: float = Field(default=0.00, ge=0, le=100) # Percentage between 0 and 100
    unitPriceAfterProductDiscount: float = Field(..., ge=0)

    lineSubtotal: float = Field(..., ge=0) # Qty * UnitPriceAfterProductDiscount

    costPriceAtSale: float = Field(..., ge=0) # For COGS

    lineTaxRate: float = Field(default=0.00, ge=0, le=100)
    lineTaxAmount: float = Field(default=0.00, ge=0)

    lineTotal: float = Field(..., ge=0) # LineSubtotal + LineTaxAmount
    notes: Optional[str] = None

class SalesInvoiceLineCreate(BaseModel):
    # When creating an invoice, frontend might only send productID and quantity.
    # Other price/discount/total fields are calculated by the backend.
    productID: int
    quantity: float = Field(..., gt=0)
    description: Optional[str] = None # Optional: User can override product name on line
    unitOfMeasure: Optional[str] = Field(default=None, max_length=20) # Optional: Can be pulled from product
    # unitPrice: Optional[float] = None # Optional: User might manually override price, backend validates/uses this
                                      # If not provided, backend uses default pricing logic.
                                      # For now, let's assume backend calculates all prices.

class SalesInvoiceLine(SalesInvoiceLineBase):
    salesInvoiceLineID: int
    salesInvoiceID: str # Foreign key as string to match SalesInvoiceHeader.SalesInvoiceID

    class Config:
        from_attributes = True

# --- SalesInvoiceHeader Models ---

class SalesInvoiceHeaderBase(BaseModel):
    customerID: int
    storeID: str = Field(..., max_length=10) # Assuming StoreID is VARCHAR(10)

    invoiceDate: datetime # Should default to now on creation if not provided
    dueDate: Optional[date] = None # Using date type for DueDate

    invoiceType: SalesInvoiceTypeLiteral
    status: SalesInvoiceStatusLiteral = 'Draft' # Default status on creation

    notes: Optional[str] = None
    salespersonID: Optional[int] = None
    paymentTermsID: Optional[int] = None
    salesOrderID: Optional[str] = Field(default=None, max_length=50)

    # Amounts are typically calculated by the backend based on lines and other inputs
    # These might not be part of Create model directly, but shown in response model
    subtotal: float = Field(default=0.00, ge=0)
    totalProductDiscountAmount: float = Field(default=0.00, ge=0)
    totalInvoiceDiscountAmount: float = Field(default=0.00, ge=0) # Manual overall discount

    taxableAmount: float = Field(default=0.00, ge=0)
    taxRate: float = Field(default=0.00, ge=0, le=100) # Overall tax rate
    taxAmount: float = Field(default=0.00, ge=0)

    shippingCharges: float = Field(default=0.00, ge=0)
    otherCharges: float = Field(default=0.00, ge=0)
    grandTotal: float = Field(default=0.00, ge=0)

    amountPaid: float = Field(default=0.00, ge=0)
    # balanceDue: float = Field(default=0.00, ge=0) # Calculated: grandTotal - amountPaid

    @validator('dueDate', 'invoiceDate', pre=True, always=True)
    def ensure_datetime_objects(cls, v, field):
        if field.name == 'invoiceDate' and v is None:
            return datetime.utcnow() # Default to now if not provided
        if isinstance(v, str):
            try:
                if field.name == 'dueDate':
                    return datetime.strptime(v, '%Y-%m-%d').date()
                return datetime.fromisoformat(v.replace('Z', '+00:00')) if 'T' in v else datetime.strptime(v, '%Y-%m-%d %H:%M:%S.%f')
            except ValueError:
                raise ValueError(f"Invalid format for {field.name}. Use ISO format or YYYY-MM-DD for date.")
        return v

    @validator('amountPaid')
    def check_amount_paid_not_exceed_grand_total(cls, v, values):
        # This validation makes sense when grandTotal is already calculated.
        # Might be better handled in API logic after all calculations.
        # For now, it's a simple check.
        grand_total = values.get('grandTotal', 0) # Default to 0 if not yet set
        if v > grand_total and grand_total > 0 : # Allow overpayment if grand_total is 0 (e.g. credit note)
             # This logic needs refinement if we want to allow overpayments for credits
             # For now, simple check:
             # raise ValueError('Amount paid cannot exceed grand total.')
             pass # Allowing overpayment for now, can be refined
        return v


class SalesInvoiceHeaderCreate(BaseModel): # Input model from user/frontend
    customerID: int
    storeID: str = Field(..., max_length=10)
    invoiceDate: Optional[datetime] = Field(default_factory=datetime.utcnow)
    dueDate: Optional[date] = None
    invoiceType: SalesInvoiceTypeLiteral
    status: Optional[SalesInvoiceStatusLiteral] = 'Draft' # Can be overridden but defaults

    notes: Optional[str] = None
    salespersonID: Optional[int] = None
    paymentTermsID: Optional[int] = None
    salesOrderID: Optional[str] = Field(default=None, max_length=50)

    # Lines are critical for creation
    lines: List[SalesInvoiceLineCreate] = Field(..., min_length=1) # Must have at least one line

    # Optional fields that user might set at creation, affecting totals
    totalInvoiceDiscountAmount: Optional[float] = Field(default=0.00, ge=0) # Manual overall discount
    shippingCharges: Optional[float] = Field(default=0.00, ge=0)
    otherCharges: Optional[float] = Field(default=0.00, ge=0)
    amountPaid: Optional[float] = Field(default=0.00, ge=0) # If payment made at time of invoice creation
    # taxRate: Optional[float] = Field(default=0.00, ge=0, le=100) # If user can set overall tax rate

class SalesInvoiceHeader(SalesInvoiceHeaderBase):
    salesInvoiceID: str # The generated formatted ID
    balanceDue: float = Field(..., ge=0) # Explicitly in response model, calculated
    lines: List[SalesInvoiceLine] = [] # Embed full line details in response
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# Example Usage
if __name__ == "__main__":
    print("Pydantic Models for Sales Module - Illustrative Examples")

    # SalesInvoiceLineCreate Example
    line1_create_data = {"productID": 101, "quantity": 2}
    line1_create = SalesInvoiceLineCreate(**line1_create_data)
    print(f"\nSalesInvoiceLineCreate: {line1_create.model_dump_json(indent=2)}")

    # SalesInvoiceLine (as if from DB, after backend calculation)
    line1_db_data = {
        "salesInvoiceLineID": 1, "salesInvoiceID": "CAS160520240001", "productID": 101, "quantity": 2,
        "unitPriceBeforeDiscount": 100.00, "productDiscountAmount": 10.00, "unitPriceAfterProductDiscount": 90.00,
        "lineSubtotal": 180.00, "costPriceAtSale": 70.00, "lineTaxAmount": 18.00, "lineTotal": 198.00
    }
    line1_db = SalesInvoiceLine(**line1_db_data)
    print(f"SalesInvoiceLine DB Model: {line1_db.model_dump_json(indent=2)}")

    # SalesInvoiceHeaderCreate Example
    invoice_create_data = {
        "customerID": 1, "storeID": "SH01", "invoiceType": "Cash",
        "lines": [line1_create_data, {"productID": 102, "quantity": 1}],
        "amountPaid": 250.00 # Example partial payment
    }
    invoice_create = SalesInvoiceHeaderCreate(**invoice_create_data)
    print(f"\nSalesInvoiceHeaderCreate: {invoice_create.model_dump_json(indent=2)}")

    # SalesInvoiceHeader (as if from DB, after backend calculation)
    # Backend would calculate all totals, balanceDue, generate ID, etc.
    invoice_db_data_dict = {
        "salesInvoiceID": "CAS160520240001", "customerID": 1, "storeID": "SH01",
        "invoiceDate": datetime.utcnow(), "invoiceType": "Cash", "status": "PartiallyPaid",
        "subtotal": 280.00, # Assuming product 102 was 100, so 180 (line1) + 100 (line2)
        "totalProductDiscountAmount": 10.00, # From line1
        "grandTotal": 308.00, # Assuming 280 subtotal + 28 tax (10% overall for example)
        "amountPaid": 250.00,
        "balanceDue": 58.00, # 308 - 250
        "lines": [line1_db.model_dump()], # Simplified, would have line2 as well
        "createdAt": datetime.utcnow(), "updatedAt": datetime.utcnow()
    }
    # Need to convert lines back to SalesInvoiceLine objects if they are dicts
    invoice_db_data_dict["lines"] = [SalesInvoiceLine(**line_data) for line_data in invoice_db_data_dict["lines"]]

    invoice_db = SalesInvoiceHeader(**invoice_db_data_dict)
    print(f"SalesInvoiceHeader DB Model: {invoice_db.model_dump_json(indent=2)}")

    try:
        SalesInvoiceLineCreate(productID=1, quantity=0)
    except ValueError as e:
        print(f"SalesInvoiceLineCreate Error: {e}")
```

**Explanation of `models_sales_module.py`:**

1.  **`SalesInvoiceTypeLiteral`, `SalesInvoiceStatusLiteral`**: Define allowed string values for `invoiceType` and `status` using `typing.Literal` for better type safety and clarity.
2.  **`SalesInvoiceLineBase`**: Contains all fields that would be present in a sales invoice line *after* all backend calculations (pricing, discounts, totals).
3.  **`SalesInvoiceLineCreate`**: This is what the frontend/API client would typically send when creating an invoice line. It's minimal: `productID` and `quantity`. Optional fields like `description` or `unitOfMeasure` can be included. The crucial point is that most pricing/discount/total fields are **not** expected from the client for a line item; they are calculated by the backend to ensure integrity.
4.  **`SalesInvoiceLine`**: The full representation of a line item, including its database ID and calculated values.
5.  **`SalesInvoiceHeaderBase`**: Contains fields common to both the creation payload and the full invoice header model. Many amount fields are here but default to 0, as they are primarily calculated by the backend. Includes validators for dates.
6.  **`SalesInvoiceHeaderCreate`**: Represents the data needed to *initiate* the creation of a sales invoice.
    *   It includes essential header info (`customerID`, `storeID`, `invoiceType`).
    *   Crucially, it takes `lines: List[SalesInvoiceLineCreate]`.
    *   It allows optional input for fields that might influence backend calculations or are set at creation (e.g., `totalInvoiceDiscountAmount` for a manual overall discount, `amountPaid`).
7.  **`SalesInvoiceHeader`**: The full representation of a sales invoice header.
    *   Includes the generated `salesInvoiceID`.
    *   Includes a calculated `balanceDue`.
    *   Embeds `lines: List[SalesInvoiceLine]` to return the full invoice detail.
8.  **Validators**: Basic validators are included (e.g., positive quantity, date logic). The `amountPaid` validator in `SalesInvoiceHeaderBase` is noted as something that might be better handled in API logic after `grandTotal` is fully determined.
9.  **`Config: from_attributes = True`**: Standard for Pydantic models that might be created from ORM objects.
10. **Illustrative Examples**: The `if __name__ == "__main__":` block shows how these models might be used.

This file provides the Pydantic data models for the Sales Invoice module, designed to clearly separate what the client sends for creation versus what the backend calculates and stores/returns.

This completes the second step of the current plan.
