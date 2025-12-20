from fastapi import FastAPI, Depends, Query
app = FastAPI()

def pagination_params(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Item per page")
):
    skip = (page - 1) * limit
    return{"page": page, "limit": limit, "skip": skip}

#Sample data
users = [f"User {i}" for i in range(1, 51)]  # 50 users

@app.get("/users")
def get_users(pagination = Depends(pagination_params)):
    start = pagination['skip']
    end = start + pagination['limit']
    return{
        "page": pagination["page"],
        "limit": pagination["limit"],
        "users": users[start:end]
    }
