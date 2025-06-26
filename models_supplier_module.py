from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, HttpUrl
from datetime import datetime

# Assuming models_product_module.py is available for Product import if needed for embedding
# from models_product_module import Product # Example if we embed full Product

# --- SupplierProduct Models (for the linking table) ---

class SupplierProductBase(BaseModel):
    productID: int # Reference to the Product's ID
    supplierProductCode: Optional[str] = Field(default=None, max_length=50)
    defaultLeadTimeDays: Optional[int] = Field(default=None, ge=0)
    lastPurchasePriceFromSupplier: Optional[float] = Field(default=None, ge=0)

class SupplierProductCreate(SupplierProductBase):
    # SupplierID will be implicitly known when creating through a supplier endpoint
    pass

class SupplierProduct(SupplierProductBase):
    supplierProductID: int # The PK of the SupplierProducts linking table itself
    supplierID: int
    # product: Optional[Product] = None # Optionally embed full Product details
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# --- Supplier Models ---

class SupplierBase(BaseModel):
    supplierName: str = Field(..., min_length=1, max_length=150)
    taxID: Optional[str] = Field(default=None, max_length=30)

    contactPerson: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    secondaryPhone: Optional[str] = Field(default=None, max_length=30)
    website: Optional[HttpUrl] = None # Validates if it's a URL

    address: Optional[str] = None
    addressLine2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=50)
    stateOrProvince: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    postalCode: Optional[str] = Field(default=None, max_length=20)

    # defaultPaymentTermsID: Optional[int] = None # Placeholder
    # defaultCurrencyID: Optional[int] = None   # Placeholder

    bankName: Optional[str] = Field(default=None, max_length=100)
    bankAccountNumber: Optional[str] = Field(default=None, max_length=50)
    bankSwiftCode: Optional[str] = Field(default=None, max_length=20)
    bankAccountHolderName: Optional[str] = Field(default=None, max_length=150)
    iban: Optional[str] = Field(default=None, max_length=50)

    isActive: bool = True
    notes: Optional[str] = None # Added based on UI design (Supplier Screen Tab 5)

class SupplierCreate(SupplierBase):
    # If creating supplier products at the same time as supplier, include them here:
    # suppliedProducts: List[SupplierProductCreate] = []
    pass

class Supplier(SupplierBase):
    supplierID: int
    # currentBalance: float = 0.00 # Typically calculated
    createdAt: datetime
    updatedAt: datetime

    # To include products supplied by this supplier when fetching a Supplier
    suppliedProducts: List[SupplierProduct] = []

    class Config:
        from_attributes = True


# Example Usage (for illustration)
if __name__ == "__main__":
    print("Pydantic Models for Supplier Module")

    # --- Supplier Examples ---
    print("\n--- Supplier Examples ---")
    supplier_create_data_valid = {
        "supplierName": "Tech Components Ltd.",
        "taxID": "SUPP-TAX-001",
        "email": "sales@techcomponents.com",
        "phone": "555-0200",
        "website": "http://techcomponents.com",
        "address": "789 Innovation Drive",
        "city": "Silicon Alley",
        "country": "USA",
        "bankName": "First National Tech Bank",
        "bankAccountNumber": "9876543210",
        "notes": "Preferred contact via email. Ask for Jane for bulk orders."
    }
    supplier_create_valid = SupplierCreate(**supplier_create_data_valid)
    print(f"SupplierCreate (valid): {supplier_create_valid.model_dump_json(indent=2)}")

    supplier_db_mock_valid = Supplier(
        supplierID=1,
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        suppliedProducts=[], # Initialize with empty list
        **supplier_create_valid.model_dump()
    )
    print(f"Supplier DB Model (valid): {supplier_db_mock_valid.model_dump_json(indent=2)}")

    try:
        SupplierCreate(supplierName="") # Invalid, empty name
    except ValueError as e:
        print(f"SupplierCreate Error (empty name): {e}")

    try:
        SupplierCreate(supplierName="Web Test", website="not-a-url")
    except ValueError as e:
        print(f"SupplierCreate Error (invalid website URL): {e}")

    # --- SupplierProduct Examples (assuming productID 101 exists) ---
    print("\n--- SupplierProduct Examples ---")
    sp_create_data_valid = {
        "productID": 101, # Assuming Product with ID 101 exists
        "supplierProductCode": "TC-DELL-XPS13",
        "defaultLeadTimeDays": 7,
        "lastPurchasePriceFromSupplier": 2150.00
    }
    sp_create_valid = SupplierProductCreate(**sp_create_data_valid)
    print(f"SupplierProductCreate (valid): {sp_create_valid.model_dump_json(indent=2)}")

    sp_db_mock_valid = SupplierProduct(
        supplierProductID=1,
        supplierID=supplier_db_mock_valid.supplierID, # Link to the supplier created above
        createdAt=datetime.now(),
        updatedAt=datetime.now(),
        **sp_create_valid.model_dump()
    )
    print(f"SupplierProduct DB Model (valid): {sp_db_mock_valid.model_dump_json(indent=2)}")

    # Add to supplier's list of supplied products
    supplier_db_mock_valid.suppliedProducts.append(sp_db_mock_valid)
    print(f"\nSupplier DB Model with Supplied Product: {supplier_db_mock_valid.model_dump_json(indent=2)}")

    try:
        SupplierProductCreate(productID=102, defaultLeadTimeDays=-5) # Invalid lead time
    except ValueError as e:
        print(f"SupplierProductCreate Error (negative lead time): {e}")
```

**Explanation of the Pydantic Models:**

*   **`SupplierProductBase`, `SupplierProductCreate`, `SupplierProduct`:**
    *   Models for the `SupplierProducts` linking table.
    *   `productID` is included to reference the product.
    *   `SupplierProduct` (the full model) includes `supplierProductID` (its own PK) and `supplierID`.
    *   A commented-out line `product: Optional[Product] = None` shows how you could embed the full `Product` object if needed in API responses, but this would require importing the `Product` model from `models_product_module.py`.
*   **`SupplierBase`, `SupplierCreate`, `Supplier`:**
    *   Models for the `Suppliers` table.
    *   Includes fields for contact details, address, bank information, and the `notes` field from the UI design.
    *   `website`: Uses `HttpUrl` for URL validation.
    *   `SupplierCreate` has a commented-out example `suppliedProducts: List[SupplierProductCreate] = []` to show how one might allow creating a supplier and linking products to them in a single API call. This would require more complex API endpoint logic.
    *   The full `Supplier` model includes `suppliedProducts: List[SupplierProduct] = []` to represent the one-to-many relationship when fetching supplier details.
*   **`Config: from_attributes = True`:** Used for compatibility with ORM objects.
*   **Illustrative `if __name__ == "__main__":` block:** Provides examples of model instantiation and validation.

This file `models_supplier_module.py` now contains the Pydantic data models for `Suppliers` and `SupplierProducts`. These models will serve for API request/response validation and as structured data representations within the application.

This completes the fourth step of the current plan.
