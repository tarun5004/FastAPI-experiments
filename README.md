# FastAPI Learning Project

## 📚 Description
This is my first FastAPI project created while learning FastAPI fundamentals. The project demonstrates basic concepts like routing, path parameters, query parameters, and working with JSON data.

## 🚀 Features
- ✅ Basic GET endpoints
- ✅ Path parameters (dynamic URLs)
- ✅ Query parameters (search & filters)
- ✅ JSON data handling
- ✅ Product search functionality
- ✅ Category-based filtering

## 📁 Project Structure
```
fast api/
├── main.py              # Main FastAPI application
├── products.json        # Sample product data
├── requirements.txt     # Python dependencies
└── README.md           # Project documentation
```

## 🛠️ Installation

### 1. Create Virtual Environment
```bash
python -m venv .venv
```

### 2. Activate Virtual Environment
```bash
# Windows PowerShell
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

## ▶️ Running the Application

### Method 1: Direct Python
```bash
python -m uvicorn main:app --reload
```

### Method 2: Using Virtual Environment
```bash
& "C:/vscode tool/fast api/.venv/Scripts/python.exe" -m uvicorn main:app --reload
```

The server will start at: `http://127.0.0.1:8000`

## 📌 API Endpoints

### 1. Home
- **URL:** `/`
- **Method:** GET
- **Description:** Welcome message

### 2. Greet User
- **URL:** `/greet/{name}`
- **Method:** GET
- **Example:** `/greet/Rahul`
- **Description:** Greets user with dynamic name

### 3. Search Products
- **URL:** `/search?query={keyword}`
- **Method:** GET
- **Example:** `/search?query=sony`
- **Description:** Search products by name

### 4. Get All Products
- **URL:** `/products`
- **Method:** GET
- **Description:** Returns all products from JSON file

### 5. Filter Products
- **URL:** `/filter?category={category}&max_price={price}`
- **Method:** GET
- **Example:** `/filter?category=electronics&max_price=30000`
- **Description:** Filter products by category and price

## 🧪 Testing the API

### Browser
Simply open these URLs in your browser:
- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/docs` (Interactive API documentation)
- `http://127.0.0.1:8000/search?query=iphone`

### Interactive Documentation
FastAPI provides automatic interactive API documentation:
- **Swagger UI:** `http://127.0.0.1:8000/docs`
- **ReDoc:** `http://127.0.0.1:8000/redoc`

## 📖 Concepts Learned

### 1. Path Parameters
Dynamic URL segments enclosed in curly braces `{}`
```python
@app.get("/greet/{name}")
def greet_user(name: str):
    return {"message": f"Hello {name}!"}
```

### 2. Query Parameters
Optional parameters passed after `?` in URL
```python
@app.get("/search")
def search_items(query: str):
    return {"search_query": query}
```

### 3. JSON File Handling
Reading data from external JSON files
```python
def load_products():
    with open('products.json') as f:
        data = json.load(f)
    return data['products']
```

## 🔧 Technologies Used
- **FastAPI** - Modern web framework for building APIs
- **Uvicorn** - ASGI server for running FastAPI
- **Python 3.13** - Programming language
- **JSON** - Data storage format

## 📝 Notes
- This is a learning project for understanding FastAPI basics
- Currently uses JSON file as mock database
- Server runs with auto-reload enabled for development

## 🎯 Future Improvements
- [ ] Add POST, PUT, DELETE methods
- [ ] Integrate real database (SQLite/PostgreSQL)
- [ ] Add Pydantic models for validation
- [ ] Implement authentication
- [ ] Add error handling
- [ ] Create frontend interface

## 👨‍💻 Author
MCA Student learning FastAPI

## 📅 Date Created
November 30, 2025
