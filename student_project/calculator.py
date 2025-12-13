from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.get("/add")
def add_numbers(a: int, b: int):
    total = a + b
    return {"result": total}

@app.get("/subtract")
def subtract_numbers (a: int, b: int):
    difference = a - b
    return {"result": difference}

@app.get("/multiply")
def multiply_numbers(a: int, b: int):
    product = a * b
    return {"result": product}

@app.get("/divide")
def divide_numbers(a: float, b: float):
    if b == 0:
        raise HTTPException(status_code=400, detail="Division by zero is not allowed.   ")
    quotient = a / b
    return {"result": quotient}