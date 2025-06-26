from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# --- CustomerGroup Models ---

class CustomerGroupBase(BaseModel):
    groupName: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None

class CustomerGroupCreate(CustomerGroupBase):
    pass

class CustomerGroup(CustomerGroupBase):
    customerGroupID: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True

# --- Customer Models ---

class CustomerBase(BaseModel):
    customerName: str = Field(..., min_length=1, max_length=150)
    customerGroupID: Optional[int] = None
    nationalID: Optional[str] = Field(default=None, max_length=30)

    contactPerson: Optional[str] = Field(default=None, max_length=100)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=30)
    secondaryPhone: Optional[str] = Field(default=None, max_length=30)

    address: Optional[str] = None
    addressLine2: Optional[str] = Field(default=None, max_length=255)
    city: Optional[str] = Field(default=None, max_length=50)
    stateOrProvince: Optional[str] = Field(default=None, max_length=50)
    country: Optional[str] = Field(default=None, max_length=50)
    postalCode: Optional[str] = Field(default=None, max_length=20)

    creditLimit: float = Field(default=0.00, ge=0)
    # defaultPaymentTermsID: Optional[int] = None
    # defaultCurrencyID: Optional[int] = None
    # defaultSalespersonID: Optional[int] = None

    isActive: bool = True
    notes: Optional[str] = None

class CustomerCreate(CustomerBase):
    pass

class Customer(CustomerBase):
    customerID: int
    createdAt: datetime
    updatedAt: datetime

    customerGroup: Optional[CustomerGroup] = None

    class Config:
        from_attributes = True
