
from typing import List, Optional
from pydantic import BaseModel, Field, HttpUrl, root_validator # For Pydantic v1
# For Pydantic v2, you might use: from pydantic import BaseModel, Field, HttpUrl, model_validator
from datetime import datetime

class CategoryBase(BaseModel):
    categoryName: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parentCategoryID: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class Category(CategoryBase):
    categoryID: int
    createdAt: datetime
    updatedAt: datetime

    class Config:
        from_attributes = True 

class ProductImageBase(BaseModel):
    imagePath: Optional[str] = Field(default=None, max_length=255)
    imageURL: Optional[HttpUrl] = None 
    isPrimaryImage: bool = False
    caption: Optional[str] = Field(default=None, max_length=255)
    sortOrder: int = 0

    # Pydantic v1 style root_validator
    @root_validator(pre=False, skip_on_failure=True) 
    def check_at_least_one_image_source(cls, values):
        image_path, image_url = values.get('imagePath'), values.get('imageURL')
        if image_path is None and image_url is None:
            raise ValueError('Either imagePath or imageURL must be provided for a product image.')
        return values
    
    # If using Pydantic v2, the validator would look like this:
    # from pydantic import model_validator
    # @model_validator(mode='after')
    # def check_at_least_one_image_source_v2(self) -> 'ProductImageBase':
    #     if self.imagePath is None and self.imageURL is None:
    #         raise ValueError('Either imagePath or imageURL must be provided.')
    #     return self

class ProductImageCreate(ProductImageBase):
    pass

class ProductImage(ProductImageBase):
    productImageID: int
    productID: int
    uploadedAt: datetime

    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=50)
    productName: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    categoryID: Optional[int] = None
    supplierID: Optional[int] = None 
    
    standardCostPrice: float = Field(default=0.00, ge=0)
    lastPurchasePrice: Optional[float] = Field(default=None, ge=0)
    shopSellingPrice: float = Field(default=0.00, ge=0)
    fieldSellingPrice: Optional[float] = Field(default=None, ge=0)
    wholesalePrice: Optional[float] = Field(default=None, ge=0)
    
    unitOfMeasure: Optional[str] = Field(default=None, max_length=20)
    reorderLevel: int = Field(default=0, ge=0)
    
    requiresExpiryDate: bool = False
    requiresBatchNumber: bool = False
    
    isActive: bool = True

class ProductCreate(ProductBase):
    pass

class Product(ProductBase):
    productID: int
    createdAt: datetime
    updatedAt: datetime
    images: List[ProductImage] = Field(default_factory=list)

    class Config:
        from_attributes = True
