from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI(title= "Todo List")

class TaskCreate(BaseModel):
    title: str
    description: str

next_id = 1
class Task(TaskCreate):
    id: int
    created_at: datetime
    updated_at: datetime
    is_completed: bool

class TaskUpdate(BaseModel):
    id: int
    title: Optional[str] = None
    description: Optional[str] = None

class DataBase:
    def __init__(self):
        self._task: Dict[int, Task] = {}

    def add(self, task: Task):
        global id
        self._task[id] = task
        generate_next_id()

    def get_tasks(self):
        return self._task

task_instance = DataBase()

def generate_next_id():
    global next_id
    next_id += 1
# Endpoints

@app.get("/")
def index():
    return {
        "message": "Todo App"
    }

@app.post("/tasks", status_code = status.HTTP_201_CREATED)
def create_task(task: TaskCreate):
    if not task.title or task.description:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = "All fields required"
        )
    global id
    new_task = Task(
        title = task.title,
        description = task.description,
        id = id,
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
        is_completed = False
    )
    generate_next_id()
    task_instance.add(task = new_task)

    return {
        "success": True,
        "data": new_task,
        "message": "Task created successfully"
    }

@app.get("/tasks")
def get_all_task():
    tasks = task_instance.get_tasks()
    return {
        "data": tasks
    }

@app.patch("/tasks/")
def partial_update(task: TaskUpdate):
    pass
    if not task.title and not task.description:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = "At least one field required"
        )