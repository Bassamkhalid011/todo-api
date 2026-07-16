from fastapi import FastAPI, HTTPException ,status
from pydantic import BaseModel

class TaskUpdate(BaseModel):
    title: str
    done: bool

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

@app.put("/tasks/{task_id}", status_code=200)
def update_task(task_id: int, updated_task: TaskUpdate):
    for i, task in enumerate(tasks):
        if task.id == task_id:
            if not updated_task.title.strip():
                raise HTTPException(status_code=400, detail="Title cannot be empty")
            tasks[i] = Task(id=task_id, title=updated_task.title, done=updated_task.done)
            return tasks[i]
    raise HTTPException(status_code=404, detail="Task not found")

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    global tasks
    task_exists = any(task.id == task_id for task in tasks)
    if not task_exists:
        raise HTTPException(status_code=404, detail="Task not found")
    tasks = [task for task in tasks if task.id != task_id]