import sqlite3
from fastapi import FastAPI, HTTPException
from models import TaskCreate, TaskUpdate

app = FastAPI()

def get_db():
    conn = sqlite3.connect("tasks.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN DEFAULT 0
        )
    """)
    # Seed sirf tab jab table empty ho
    count = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
    if count == 0:
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Task 1", False))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Task 2", False))
        conn.execute("INSERT INTO tasks (title, done) VALUES (?, ?)", ("Task 3", False))
        conn.commit()
    conn.close()

init_db()

@app.get("/")
def read_root():
    return {
        "name": "Bassam",
        "version": "1.0",
        "description": "This is a simple FastAPI application.",
        "endpoints": ["/tasks"]
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tasks")
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks").fetchall()
    conn.close()
    return [dict(task) for task in tasks]

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return dict(task)

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)", 
        (task.title, False)
    )
    conn.commit()
    new_task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", 
        (cursor.lastrowid,)
    ).fetchone()
    conn.close()
    return dict(new_task)

@app.put("/tasks/{task_id}", status_code=200)
def update_task(task_id: int, updated_task: TaskUpdate):
    if not updated_task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (updated_task.title, updated_task.done, task_id)
    )
    conn.commit()
    updated = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(updated)

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    conn = get_db()
    task = conn.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if task is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found")
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()