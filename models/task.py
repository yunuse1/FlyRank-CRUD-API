from pydantic import BaseModel
from typing import Optional

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
