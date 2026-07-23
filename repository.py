import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from models.task import TaskCreate, TaskUpdate

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class PostgresTaskRepository:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
    
    def close(self):
        self.conn.close()

    def get_all_tasks(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]

    def get_task_by_id(self, task_id: int):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT * FROM tasks WHERE id = %s", (task_id,))
        row = cur.fetchone()
        return dict(row) if row else None

    def create_task(self, task: TaskCreate):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done", (task.title, task.done))
        row = cur.fetchone()
        self.conn.commit()
        cur.close()
        return dict(row) if row else None

    def update_task(self, task_id: int, task: TaskUpdate):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("UPDATE tasks SET title=%s , done=%s WHERE id=%s RETURNING id, title, done", (task.title, task.done, task_id))
        row = cur.fetchone()
        self.conn.commit()
        cur.close()
        return dict(row) if row else None
        
    def delete_task(self, task_id: int):
        cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur.execute("DELETE FROM tasks WHERE id =%s RETURNING id", (task_id,))
        row = cur.fetchone()
        self.conn.commit()
        cur.close()
        return dict(row) if row else None

    def reset_task(self):
        cur = self.conn.cursor(cursor_factory = psycopg2.extras.RealDictCursor)
        cur.execute("DELETE FROM tasks")
        self.conn.commit()
        cur.close()

    def count_tasks(self):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("SELECT COUNT(*) AS count FROM tasks")
        total = cur.fetchone()["count"]
        cur.execute("SELECT COUNT(*) AS count FROM tasks WHERE done = true")
        completed = cur.fetchone()["count"]
        pending = total - completed
        cur.close()
        return {"total_tasks": total, "completed_tasks": completed, "pending_tasks": pending}

