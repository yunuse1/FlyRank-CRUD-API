from typing import Optional

from fastapi import FastAPI, HTTPException, status, Response
from pydantic import BaseModel
import sqlite3

app = FastAPI()

DB_FILE = "tasks.db"

connection_obj = sqlite3.connect(DB_FILE, check_same_thread=False)
connection_obj.row_factory = sqlite3.Row
cursor_obj = connection_obj.cursor()

def init_db():
    cursor_obj.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)
    
    cursor_obj.execute("SELECT COUNT(*) FROM tasks")
    count = cursor_obj.fetchone()[0]
    
    if count == 0:
        cursor_obj.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Hello", False))
        cursor_obj.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Task", True))
        cursor_obj.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Backend", False))
        
    connection_obj.commit()

init_db()

tasks = [
    {"id": 1, "title": "Hello", "done": False},
    {"id": 2, "title": "Task", "done": True},
    {"id": 3, "title": "Backend", "done": False}
]
tasks_list = list(tasks)


class Task(BaseModel):
    """
    Data model for a task, including its title, completion status, and optional ID.
    """
    id: int
    title: str
    done: bool = False

class TaskCreate(BaseModel):
    """
    Data model for creating a task, requires a title and allows an optional done status.
    """
    title: str
    done: bool = False

class TaskUpdate(BaseModel):
    """
    Data model for updating a task, allowing optional updates to title and/or completion status.
    """
    title: Optional[str] = None
    done: Optional[bool] = None


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
    cursor_obj.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    row = cursor_obj.fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return dict(row)

@app.get("/tasks", response_model=list[Task])
def search_tasks(search: Optional[str] = None, done: Optional[bool] = None):
    """
    Endpoint to search for tasks based on title and/or completion status.
    """
    query = "SELECT * FROM tasks WHERE 1=1"
    params = []
    if search is not None:
        query += " AND title LIKE ?"
        params.append(f"%{search}%")
    if done is not None:
        query += " AND done = ?"
        params.append(done)
        
    cursor_obj.execute(query, params)
    rows = cursor_obj.fetchall()
    if not rows:
        raise HTTPException(status_code=404, detail="No tasks found matching the criteria")
    return [dict(row) for row in rows]

@app.get("/stats")
def get_stats():
    """
    Endpoint to retrieve statistics about the tasks.
    """
    return {
        "total_tasks": len(tasks),
        "completed_tasks": len([task for task in tasks if task["done"]]),
        "pending_tasks": len([task for task in tasks if not task["done"]])
    }

@app.post("/reset")
def reset_tasks():
    """
    Endpoint to reset the list of tasks to its initial state.
    """
    global tasks
    tasks = tasks_list.copy()
    return { "message": "Tasks have been reset", "tasks": tasks }

@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(task_input: TaskCreate):
    """
    Endpoint to create a new task.
    """
    if not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title is required")
    
    next_id = max([task["id"] for task in tasks]) + 1 if tasks else 1
    new_task = {
        "id": next_id,
        "title": task_input.title,
        "done": task_input.done
    }
    tasks.append(new_task)
    return new_task

@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_input: TaskUpdate):
    """
    Endpoint to update an existing task by its ID.
    """
    if task_input.title is not None and not task_input.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty or whitespaces only")
    
    for task in tasks:
        if task["id"] == task_id:
            if task_input.title is not None:
                task["title"] = task_input.title
            if task_input.done is not None:
                task["done"] = task_input.done
            return task
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