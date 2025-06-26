
from typing import Optional, List, Any 
from pydantic import BaseModel, Field, EmailStr 
from datetime import datetime

# --- SupplierProduct Models (for the linking table) ---

class SupplierProductBase(BaseModel):
    productID: int 
    supplierProductCode: Optional[str] = Field(default=None, max_length=50)
    defaultLeadTimeDays: Optional[int] = Field(default=None, ge=0) 
    lastPurchasePriceFromSupplier: Optional[float] = Field(default=None, ge=0)

class SupplierProductCreate(SupplierProductBase):
    pass

class SupplierProduct(SupplierProductBase):
    supplierProductID: int 
    supplierID: int 
    # product: Optional[Any] = None # Placeholder for potential Product model embedding
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
    website: Optional[str] = Field(default=None, max_length=255) 

    address: Optional[str] = None
    addressLine2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=50)
    stateOrProvince: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    postalCode: Optional[str] = Field(default=None, max_length=20)
  
    bankName: Optional[str] = Field(default=None, max_length=100)
    bankAccountNumber: Optional[str] = Field(default=None, max_length=50)
    bankSwiftCode: Optional[str] = Field(default=None, max_length=20)
    bankAccountHolderName: Optional[str] = Field(default=None, max_length=150)
    iban: Optional[str] = Field(default=None, max_length=50)
    
    isActive: bool = True
    notes: Optional[str] = None 

class SupplierCreate(SupplierBase):
    pass

class Supplier(SupplierBase):
    supplierID: int
    createdAt: datetime
    updatedAt: datetime
    
    suppliedProducts: List[SupplierProduct] = Field(default_factory=list) 

    class Config:
        from_attributes = True
