from fastapi import APIRouter

router = APIRouter()

#Get all users
@router.get("/")
def get_users():
    return ["Tarun","Ankita","John"]

#get single user by ID
@router.get("/{user_id}")
def get_user(user_id: int):
    return {"user_id": user_id, "name": f"user {user_id}"}

