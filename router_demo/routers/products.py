from fastapi import APIRouter, HTTPException
router = APIRouter()

#Fake Database
products_db = [
    {"id": 1, "name": "Laptop", "category": "Electronics", "price": 1000},
    {"id": 2, "name": "Smartphone", "category": "Electronics", "price": 500},
    {"id": 3, "name": "T-shirt", "category": "Clothing", "price": 20},
    {"id": 4, "name": "Jeans", "category": "Clothing", "price": 40},
]

#Get all products
@router.get("/")
def get_all_products():
    return {"products": products_db}

#Get single product by ID
@router.get("/{product_id}")
def get_product(product_id: int):
    for product in products_db:
        if product['id'] == product_id:
            return product
    raise HTTPException(status_code=404, detail="Product not found")
        
@router.post("/")
def create_product(name: str, price: int, category: str):
    """Create a new product"""
    new_product = {
        "id" : len(products_db) + 1, 
        "name" : name, 
        "category": category, 
        "price": price
    }
    products_db.append(new_product)
    return new_product