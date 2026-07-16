from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel


app = FastAPI()

tasks = [
    {"id": 1, "title": "Hello", "done": False},
    {"id": 2, "title": "Task", "done": True},
    {"id": 3, "title": "Backend", "done": False}
]

class Task(BaseModel):
    """
    Data model for a task, including its title, completion status, and optional ID.
    """
    title: str
    done: bool = False
    id: int = None

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

@app.get("/tasks")
def get_all_tasks():
    """
    Endpoint to retrieve all tasks.
    """
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    """
    Endpoint to retrieve a specific task by its ID.
    """
    for task in tasks:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks")
def create_task(task: Task):
    """
    Endpoint to create a new task.
    """
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    next_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task = {
        "id": next_id,
        "title": task.title,
        "done": task.done
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: Task):
    """
    Endpoint to update an existing task by its ID.
    """

    if task.title is not None and not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespaces only")
    
    for index, item in enumerate(tasks):
        if item["id"] is None:
            raise HTTPException(status_code=400, detail="Task ID is required")
        if item["id"] == task_id:
            tasks[index]["title"] = task.title
            tasks[index]["done"] = task.done
            return tasks[index]
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    """
    Endpoint to delete a specific task by its ID.
    """

    for index, item in enumerate(tasks):
        if item["id"] == task_id:
            tasks.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")