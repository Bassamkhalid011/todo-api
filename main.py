from fastapi import FastAPI, HTTPException
app=FastAPI()
tasks=[{"id": 1, "title": "Task 1", "done": True},
      {"id": 2, "title": "Task 2", "done": False},
      {"id": 3, "title": "Task 3", "done": False}]
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
        if task["id"] == task_id:
            return task
    raise HTTPException(status_code=404, detail="Task not found")