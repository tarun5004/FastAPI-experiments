from fastapi import FastAPI

import asyncio

app = FastAPI()

@app.get("/slow")
async def slow_response():
    """Simulate a slow response using asyncio.sleep"""
    await asyncio.sleep(3)
    return {"message": "Done after 3 seconds"}

#parallel endpoint to demonstrate async behavior using asyncio.gather
@app.get("/dashboard")     
async def fetch_users():
    await asyncio.sleep(2) # Simulate 2 sec DB call
    return {"users": ["Alice", "Bob", "Charlie"]}

async def fetch_orders():
    await asyncio.sleep(2) # Simulate 2 sec DB call
    return {"orders": [101, 102, 103]}

async def fetch_inventory():
    await asyncio.sleep(2)  # Simulate 2 sec DB call
    return {"inventory": ["item1", "item2", "item3"]}

@app.get("/dashboard/complete")
async def complete_dashboard():
    await asyncio.gather(
        fetch_users(),  fetch_orders(), fetch_inventory()
    )
    return {
        "users": ["Alice", "Bob", "Charlie"],
        "orders": [101, 102, 103],
        "inventory": ["item1", "item2", "item3"]
    }
