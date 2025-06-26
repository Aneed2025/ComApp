
from fastapi import FastAPI, HTTPException, APIRouter, Path, Body, status, UploadFile, File, Form
from typing import List, Optional
from datetime import datetime

# Assuming models_product_module.py is in a directory accessible by PYTHONPATH
# For the structure app/models/ and app/apis/, with main_api.py in app/:
from ..models.models_product_module import (
    Category, CategoryCreate,
    Product, ProductCreate,
    ProductImage, ProductImageCreate, ProductImageBase
)

# Mock Database
# IMPORTANT: When integrated into main_api.py, this local mock_db will be
# superseded by the shared_mock_db instance from main_api.py.
mock_db = {
    "categories": {
        1: Category(categoryID=1, categoryName="Default Category", description="Initial default category", parentCategoryID=None, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow())
    },
    "products": {},
    "product_images": {},
    "next_category_id": 2,
    "next_product_id": 1,
    "next_product_image_id": 1,
}

router = APIRouter(
    prefix="/api/v1",
    tags=["Products Module"]
)

# --- Categories Endpoints ---
@router.post("/categories", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category_endpoint(category_in: CategoryCreate):
    if any(c.categoryName.lower() == category_in.categoryName.lower() for c in mock_db["categories"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    if category_in.parentCategoryID and category_in.parentCategoryID not in mock_db["categories"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent CategoryID '{category_in.parentCategoryID}' not found")
    
    new_id = mock_db["next_category_id"]
    db_category = Category(
        categoryID=new_id,
        createdAt=datetime.utcnow(),
        updatedAt=datetime.utcnow(),
        **category_in.model_dump()
    )
    mock_db["categories"][new_id] = db_category
    mock_db["next_category_id"] += 1
    return db_category

@router.get("/categories", response_model=List[Category])
async def get_all_categories_endpoint(skip: int = 0, limit: int = 100):
    categories_list = list(mock_db["categories"].values())
    return categories_list[skip : skip + limit]

@router.get("/categories/{category_id}", response_model=Category)
async def get_category_by_id_endpoint(category_id: int = Path(..., title="The ID of the category to get")):
    category = mock_db["categories"].get(category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    return category

@router.put("/categories/{category_id}", response_model=Category)
async def update_category_endpoint(
    category_id: int = Path(..., title="The ID of the category to update"),
    category_in: CategoryCreate = Body(...)
):
    if category_id not in mock_db["categories"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    current_category = mock_db["categories"][category_id]
    if category_in.categoryName.lower() != current_category.categoryName.lower() and \
       any(c.categoryName.lower() == category_in.categoryName.lower() for c_id, c in mock_db["categories"].items() if c_id != category_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")
    if category_in.parentCategoryID and category_in.parentCategoryID not in mock_db["categories"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Parent CategoryID '{category_in.parentCategoryID}' not found")
    if category_in.parentCategoryID == category_id: 
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category cannot be its own parent.")
    updated_category_data = category_in.model_dump(exclude_unset=True)
    updated_category = current_category.model_copy(update=updated_category_data) 
    updated_category.updatedAt = datetime.utcnow()
    mock_db["categories"][category_id] = updated_category
    return updated_category

@router.delete("/categories/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category_endpoint(category_id: int = Path(..., title="The ID of the category to delete")):
    if category_id not in mock_db["categories"]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")
    if any(p.categoryID == category_id for p in mock_db["products"].values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category is in use by products.")
    if any(c.parentCategoryID == category_id for c in mock_db["categories"].values()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Category is a parent to other categories.")
    del mock_db["categories"][category_id]

# --- Products Endpoints ---
@router.post("/products", response_model=Product, status_code=status.HTTP_201_CREATED)
async def create_product_endpoint(product_in: ProductCreate):
    if any(p.sku.lower() == product_in.sku.lower() for p in mock_db["products"].values()):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{product_in.sku}' already exists")
    if product_in.categoryID and product_in.categoryID not in mock_db["categories"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CategoryID '{product_in.categoryID}' not found")
    new_id = mock_db["next_product_id"]
    db_product = Product(productID=new_id, createdAt=datetime.utcnow(), updatedAt=datetime.utcnow(), images=[], **product_in.model_dump())
    mock_db["products"][new_id] = db_product
    mock_db["next_product_id"] += 1
    return db_product

@router.get("/products", response_model=List[Product])
async def get_all_products_endpoint(skip: int = 0, limit: int = 10, category_id: Optional[int] = None, name: Optional[str] = None, sku: Optional[str] = None):
    results = list(mock_db["products"].values())
    if category_id is not None: results = [p for p in results if p.categoryID == category_id]
    if name: results = [p for p in results if name.lower() in p.productName.lower()]
    if sku: results = [p for p in results if p.sku and sku.lower() == p.sku.lower()]
    response_list = []
    for prod_data in results[skip : skip + limit]:
        images = [img for img in mock_db["product_images"].values() if img.productID == prod_data.productID]
        temp_prod_dict = prod_data.model_dump(); temp_prod_dict['images'] = images
        response_list.append(Product(**temp_prod_dict))
    return response_list

@router.get("/products/{product_id}", response_model=Product)
async def get_product_by_id_endpoint(product_id: int = Path(..., title="The ID of the product")):
    product_item = mock_db["products"].get(product_id) 
    if not product_item: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    images = [img for img in mock_db["product_images"].values() if img.productID == product_id]
    temp_prod_dict = product_item.model_dump(); temp_prod_dict['images'] = images
    return Product(**temp_prod_dict)

@router.put("/products/{product_id}", response_model=Product)
async def update_product_endpoint(product_id: int = Path(..., title="The ID of the product"), product_in: ProductCreate = Body(...)):
    if product_id not in mock_db["products"]: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    current_product = mock_db["products"][product_id]
    if product_in.sku.lower() != current_product.sku.lower() and \
       any(p.sku.lower() == product_in.sku.lower() for pid, p in mock_db["products"].items() if pid != product_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"SKU '{product_in.sku}' already exists")
    if product_in.categoryID and product_in.categoryID not in mock_db["categories"]:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"CategoryID '{product_in.categoryID}' not found")
    updated_product_data = product_in.model_dump(exclude_unset=True)
    updated_product = current_product.model_copy(update=updated_product_data)
    updated_product.updatedAt = datetime.utcnow()
    mock_db["products"][product_id] = updated_product
    images = [img for img in mock_db["product_images"].values() if img.productID == product_id]
    temp_prod_dict = updated_product.model_dump(); temp_prod_dict['images'] = images
    return Product(**temp_prod_dict)

@router.delete("/products/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_endpoint(product_id: int = Path(..., title="The ID of the product")):
    if product_id not in mock_db["products"]: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    img_ids_to_delete = [img_id for img_id, img in mock_db["product_images"].items() if img.productID == product_id]
    for img_id in img_ids_to_delete: del mock_db["product_images"][img_id]
    del mock_db["products"][product_id]

# --- Product Images Endpoints ---
@router.post("/products/{product_id}/images", response_model=ProductImage, status_code=status.HTTP_201_CREATED)
async def add_product_image_endpoint(product_id: int = Path(..., title="Product ID"), image_in: ProductImageCreate = Body(...)):
    if product_id not in mock_db["products"]: raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    if image_in.isPrimaryImage:
        for img in mock_db["product_images"].values():
            if img.productID == product_id and img.isPrimaryImage: img.isPrimaryImage = False 
    new_id = mock_db["next_product_image_id"]
    db_image = ProductImage(productImageID=new_id, productID=product_id, uploadedAt=datetime.utcnow(), **image_in.model_dump())
    mock_db["product_images"][new_id] = db_image
    mock_db["next_product_image_id"] += 1
    return db_image

@router.put("/products/{product_id}/images/{image_id}", response_model=ProductImage)
async def update_product_image_details_endpoint(product_id: int = Path(..., title="Product ID"), image_id: int = Path(..., title="Image ID"), image_in: ProductImageBase = Body(...)):
    if product_id not in mock_db["products"]: raise HTTPException(status_code=404, detail="Product not found")
    if image_id not in mock_db["product_images"] or mock_db["product_images"][image_id].productID != product_id:
        raise HTTPException(status_code=404, detail="Image not found for this product")
    current_image = mock_db["product_images"][image_id]
    if image_in.isPrimaryImage and not current_image.isPrimaryImage: 
        for img in mock_db["product_images"].values():
            if img.productID == product_id and img.isPrimaryImage and img.productImageID != image_id: img.isPrimaryImage = False 
    updated_image_data = image_in.model_dump(exclude_unset=True)
    updated_image = current_image.model_copy(update=updated_image_data)
    mock_db["product_images"][image_id] = updated_image
    return updated_image

@router.delete("/products/{product_id}/images/{image_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_image_endpoint(product_id: int = Path(..., title="Product ID"), image_id: int = Path(..., title="Image ID")):
    if image_id not in mock_db["product_images"] or mock_db["product_images"][image_id].productID != product_id:
        raise HTTPException(status_code=404, detail="Image not found for this product")
    del mock_db["product_images"][image_id]
