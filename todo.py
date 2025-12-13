from fastapi import FastAPI
from pydantic import BaseModel

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
@app.post("/todos")
def add_todo(todo: Todo):
    new_todo ={
        "id": len(todos) + 1,
        "task": todo.task,
        "done": False
    }
    todos.append(new_todo)
    return new_todo