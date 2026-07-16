from fastapi import FastAPI, HTTPException ,status
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str
    


class Task(BaseModel):
    id: int
    title: str
    done: bool

app=FastAPI()
tasks=[Task(id=1, title="Task 1", done=True),
      Task(id=2, title="Task 2", done=False),
      Task(id=3, title="Task 3", done=False)]
      
@app.get("/")
def read_root():
    return {"name": "Bassam",
            "version": "1.0",
            "description": "This is a simple FastAPI application.",
            "endpoints": ["/tasks"]}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/tasks")
def get_tasks():
    return tasks
    

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Title cannot be empty")

    new_task = Task(id=len(tasks) + 1, title=task.title, done=False)
    tasks.append(new_task)

    return new_task