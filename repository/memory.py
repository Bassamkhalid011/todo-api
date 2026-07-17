from models import Task
from repository.base import TaskRepository

class InMemoryRepository(TaskRepository):
    
    def __init__(self):
        self.tasks = [
            Task(id=1, title="Task 1", done=True),
            Task(id=2, title="Task 2", done=False),
            Task(id=3, title="Task 3", done=False)
        ]
    
    def get_all(self):
        return self.tasks
    
    def get_by_id(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def create(self, title: str):
        new_task = Task(
            id=len(self.tasks) + 1,
            title=title,
            done=False
        )
        self.tasks.append(new_task)
        return new_task
    
    def update(self, task_id: int, title: str, done: bool):
        for i, task in enumerate(self.tasks):
            if task.id == task_id:
                self.tasks[i] = Task(id=task_id, title=title, done=done)
                return self.tasks[i]
        return None
    
    def delete(self, task_id: int):
        self.tasks = [task for task in self.tasks if task.id != task_id]