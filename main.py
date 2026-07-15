from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel


app = FastAPI()

tasks = [
    {"id": 1, "title": "Hello", "done": False},
    {"id": 2, "title": "Task", "done": True},
    {"id": 3, "title": "Backend", "done": False}
]

@app.get("/")
async def root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health")
def check_health():
    return { "status": "ok" }

@app.get("/tasks")
def get_all_tasks():
    return tasks

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task
    return {"error": "Task not found"}

@app.post("/tasks")
def create_task(task: dict):
    if not task.get("title"):
        return {"error": status.HTTP_400_BAD_REQUEST, "message": "Title is required"}
    
    new_task = {
        "id": len(tasks) + 1,
        "title": task.get("title", ""),
        "done": task.get("done", False)
    }
    tasks.append(new_task)
    return new_task