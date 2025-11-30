from fastapi import FastAPI
import json

app = FastAPI()

@app.get("/")
def welcome():
    return {"message": "This is my first FastAPI project!"}


#Path Parameter example

@app.get("/greet/{name}")
def greet_user(name: str):
    return {"message": f"Hello, {name}"}

#Query Parameter example

def load_products():
    with open('products.json') as f:
        data = json.load(f)
    return data['products']    

@app.get("/search")
def search_items(query: str):
    products = load_products()
    
    query_lower = query.lower()  # Convert query to lowercase for case-insensitive comparison
    results = []
    
    for product in products:
        if query_lower in product['name'].lower():  # Case-insensitive search (convert product name to lowercase)
            results.append(product)
            
    return {
        "search_query": query,
        "found_items": len(results),
        "results": results
    }
            
            
#Category Filter example

@app.get("/filter_by_category/")
def filter_products(category: str, max_price: int = None):
    products = load_products()
    results = []
    
    for product in products:
        if product ['category'] == category:
            if max_price is None or product['price'] <= max_price:
                results.append(product)
            else:
                results.append(product)


    return {
    "category": category,
    "max_price": max_price, 
    "found": len(results),
    "results": results
}    