from repository.base import TaskRepository

class TaskService:
    
    def __init__(self, repository: TaskRepository):
        self.repository = repository
    
    def get_all_tasks(self):
        return self.repository.get_all()
    
    def get_task(self, task_id: int):
        task = self.repository.get_by_id(task_id)
        if task is None:
            return None
        return task
    
    def create_task(self, title: str):
        if not title.strip():
            raise ValueError("Title cannot be empty")
        return self.repository.create(title)
    
    def update_task(self, task_id: int, title: str, done: bool):
        if not title.strip():
            raise ValueError("Title cannot be empty")
        return self.repository.update(task_id, title, done)
    
    def delete_task(self, task_id: int):
        return self.repository.delete(task_id)