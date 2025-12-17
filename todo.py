from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import HTTPException, status 

app = FastAPI()

#Storage (in memory list)
todos = []

# Pydantic model for Todo item - Blueprint for data validation
class TodoItem(BaseModel):
    task: str
    
# GET all todo items

@app.get("/todos")
def get_todos():
    return todos

# POST a new todo item
@app.post("/todos", status_code=status.HTTP_201_CREATED)
def add_todo(todo: TodoItem):
    new_todo ={
        "id": len(todos) + 1,
        "task": todo.task,
        "done": False
    } 
    todos.append(new_todo)
    return new_todo



# Delete a todo item by ID
@app.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: int):
    for todo in todos:
        if todo['id'] == todo_id:
            todos.remove(todo)
            return None  # 204 No Content - no body returned
        
    raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} not found")

class TodoUpdate(BaseModel):
    task: str = None  # Optional field
    done: bool = None  # Optional field
# Update a todo item by ID
@app.put("/todos/{todo_id}")
def update_todo(todo_id: int, update: TodoUpdate):
    for todo in todos:
        if todo['id'] == todo_id:
            if update.task is not None:
                todo['task'] = update.task
            if update.done is not None:
                todo['done'] = update.done
            return todo
    raise HTTPException(status_code=404, detail=f"Todo item with ID {todo_id} not found")

