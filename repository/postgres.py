import psycopg2
import os
from models import Task
from repository.base import TaskRepository

class PostgresRepository(TaskRepository):
    
    def __init__(self):
        self.conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        self.conn.autocommit = True
    
    def get_all(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks")
        rows = cursor.fetchall()
        return [Task(id=row[0], title=row[1], done=row[2]) for row in rows]
    
    def get_by_id(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, title, done FROM tasks WHERE id = %s", (task_id,))
        row = cursor.fetchone()
        if row is None:
            return None
        return Task(id=row[0], title=row[1], done=row[2])
    
    def create(self, title: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (title, done) VALUES (%s, %s) RETURNING id, title, done",
            (title, False)
        )
        row = cursor.fetchone()
        return Task(id=row[0], title=row[1], done=row[2])
    
    def update(self, task_id: int, title: str, done: bool):
        cursor = self.conn.cursor()
        cursor.execute(
            "UPDATE tasks SET title = %s, done = %s WHERE id = %s RETURNING id, title, done",
            (title, done, task_id)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return Task(id=row[0], title=row[1], done=row[2])
    
    def delete(self, task_id: int):
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = %s", (task_id,))