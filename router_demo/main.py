from fastapi import FastAPI
from routers import users, products

app = FastAPI()
title= "My Shop API"
description= "A simple API for my shop"

# connect routers
app.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

app.include_router(
    products.router,
    prefix="/products",
    tags=["Products"]
)

@app.get("/")
def root():
    return {"message": "Welcome to My Shop API"}