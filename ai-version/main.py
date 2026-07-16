from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(
    title="Task API (AI Reference Version - Rematch)",
    description="This API is the version that fully complies with the response_model and data isolation rules following the second prompt (rematch).",
    version="1.1.0"
)

INITIAL_TASKS = [
    {"id": 1, "title": "Buy milk", "done": False},
    {"id": 2, "title": "Clean the room", "done": True},
    {"id": 3, "title": "Read a book", "done": False}
]

tasks_db = [item.copy() for item in INITIAL_TASKS]

# --- PYDANTIC SCHEMAS ---

class TaskResponse(BaseModel):
    id: int
    title: str
    done: bool

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, description="Task title cannot be empty")

class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, description="Updated title cannot be empty")
    done: Optional[bool] = None

# --- ENDPOINTS ---

@app.get("/", tags=["System"])
def read_root():
    return { "name": "Task API", "version": "1.0", "endpoints": ["/tasks"] }

@app.get("/health", tags=["System"])
def check_health():
    return { "status": "ok" }

@app.get("/tasks", response_model=list[TaskResponse], tags=["Management"])
def get_all_tasks(search: Optional[str] = None, done: Optional[bool] = None):
    filtered_tasks = tasks_db
    if search is not None:
        filtered_tasks = [task for task in filtered_tasks if search.lower() in task["title"].lower()]
    if done is not None:
        filtered_tasks = [task for task in filtered_tasks if task["done"] == done]
    return filtered_tasks

@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["Management"])
def get_single_task(task_id: int):
    for task in tasks_db:
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.post("/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Management"])
def create_task(task_input: TaskCreate):
    if not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespaces only")
        
    next_id = max([task["id"] for task in tasks_db]) + 1 if tasks_db else 1
    new_task = {
        "id": next_id,
        "title": task_input.title,
        "done": False
    }
    tasks_db.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["Management"])
def update_task(task_id: int, task_input: TaskUpdate):
    if task_input.title is not None and not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespaces only")

    for task in tasks_db:
        if task["id"] == task_id:
            if task_input.title is not None:
                task["title"] = task_input.title
            if task_input.done is not None:
                task["done"] = task_input.done
            return task
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Management"])
def delete_task(task_id: int):
    for index, task in enumerate(tasks_db):
        if task["id"] == task_id:
            tasks_db.pop(index)
            return Response(status_code=status.HTTP_204_NO_CONTENT)
            
    raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@app.get("/stats", tags=["Statistics"])
def get_stats():
    total = len(tasks_db)
    done_count = sum(1 for task in tasks_db if task["done"])
    return {
        "total": total,
        "done": done_count,
        "open": total - done_count
    }

@app.post("/reset", tags=["System"])
def reset_tasks():
    global tasks_db
    tasks_db = [item.copy() for item in INITIAL_TASKS]
    return {"message": "Database reset to initial state", "tasks": tasks_db}