from fastapi import FastAPI, Depends
app = FastAPI()

# Dependency 1: Database
def get_db():
    return {"db_connection": "connected"}

# Dependency 2: Current User
def get_current_user():
    return {"user_id": 1, "name": "Test User"}

#Dependency 3:Settings
def get_settings():
    return {"theme": "dark"}

# All three dependencies used in the endpoint
@app.get("/dashboard")
def dashboard(
    db = Depends(get_db),
    user = Depends(get_current_user),
    settings = Depends(get_settings)
):
    return {
        "db": db,
        "user": user,
        "settings": settings
    }