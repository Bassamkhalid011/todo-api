from fastapi import FastAPI, HTTPException, status
from models import TaskCreate, TaskUpdate
from repository.postgres import PostgresRepository

from service import TaskService
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()
repository = PostgresRepository()
service = TaskService(repository)

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
    return service.get_all_tasks()

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):
    try:
        return service.create_task(task.title)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.put("/tasks/{task_id}", status_code=200)
def update_task(task_id: int, updated_task: TaskUpdate):
    try:
        task = service.update_task(task_id, updated_task.title, updated_task.done)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found")
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):
    task = service.get_task(task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    service.delete_task(task_id)