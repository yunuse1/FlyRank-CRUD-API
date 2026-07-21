import psycopg2
import os
from dotenv import load_dotenv
import psycopg2
from pydantic import BaseModel

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class PostgresTaskRepository:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.row_factory = psycopg2.extras.DictRow
    
    def close(self):
        self.conn.close()

    def get_all_tasks(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks")
        rows = cur.fetchall()
        cur.close()
        return [dict(row) for row in rows]

    def get_task_by_id(self, task_id: int):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cur.fetchone()
        cur.close()
        return dict(row) if row else None
    
    


