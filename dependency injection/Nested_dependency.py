from fastapi import FastAPI, Depends

app = FastAPI()

# Level 1: Sabse pehle ye chalega
def get_db():
    print("Step 1: DB connected")
    return {"connection": "MySQL"}

# Level 2: Phir ye chalega
def get_user_from_db(db = Depends(get_db)):
    print("Step 2: Fetching user from DB")
    return {"user_id": 43, "name": "John Doe"}

# Level 3: Ye get_user_from_db pe depend karta hai
def get_user_permissions(user_data = Depends(get_user_from_db)):
    print("step 3: permission fetch ")
    return {"user_id": user_data, "permissions":["read", "write"]}

#endpoint

@app.get("/profile")
def profile(data = Depends(get_user_permissions)):
    return data