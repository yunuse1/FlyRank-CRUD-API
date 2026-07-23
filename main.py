from typing import Optional

from fastapi import FastAPI, HTTPException, status, Response
from repository import PostgresTaskRepository
from models.task import Task, TaskCreate, TaskUpdate

app = FastAPI()

DB_FILE = "tasks.db"

repository = PostgresTaskRepository()

@app.get("/")
async def root():
    """
    Root endpoint that provides basic information about the API.
    """       
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def check_health():
    """
    Endpoint to check the health status of the API.
    """
    return { "status": "ok" }

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Endpoint to retrieve a specific task by its ID.
    """
    row = repository.get_task_by_id(task_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(row)

@app.get("/tasks", response_model=list[Task])
def search_tasks(search: Optional[str] = None, done: Optional[bool] = None):
    """
    Endpoint to search for tasks based on title and/or completion status.
    """
    tasks = repository.get_all_tasks()
    if search is not None:
        tasks = [task for task in tasks if search in task["title"]]
    if done is not None:
        tasks = [task for task in tasks if task["done"] == done]        
    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found matching the criteria")
    return tasks

@app.get("/stats")
def get_stats():
    """
    Endpoint to retrieve statistics about the tasks.
    """
    return repository.count_tasks()

@app.post("/reset")
def reset_tasks():
    """
    Endpoint to reset the list of tasks to its initial state.
    """
    repository.reset_task()
    return { "message": "Tasks have been reset" }

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_input: TaskCreate):
    """
    Endpoint to create a new task.
    """
    rows = repository.create_task(task_input)
    if rows is None:
        raise HTTPException(status_code=400, detail="Title is required")
    return dict(rows)        
    
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_input: TaskUpdate):
    """
    Endpoint to update an existing task by its ID.
    """
    if task_input.title is not None and not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespaces only")
    
    if task_id is None:
        raise HTTPException(status_code=400, detail="Task ID cannot be empty")
    
    row = repository.update_task(task_id, task_input)
    return dict(row)

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Endpoint to delete a specific task by its ID.
    """

    row = repository.get_task_by_id(task_id)
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

    repository.delete_task(task_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)