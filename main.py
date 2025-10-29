from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from datetime import datetime
from typing import List, Dict, Optional

app = FastAPI(title= "Todo List")

class User(BaseModel):
    username: str

class UserCreate(User):
    password: str

class UserInDb(User):
    created_at: datetime
    updated_at: datetime

class UserResponse(User):
    created_at: datetime
    updated_at: datetime

class TaskCreate(BaseModel):
    title: str
    description: str

class TaskInDb(TaskCreate):
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
        # Two tables
        self._users: Dict[int, UserInDb] = {}
        self._task: Dict[int, List[TaskInDb]] = {}
        self.id_task = 1
        self.user_id = 1

    def add_task(self, user_id: int, task: TaskInDb):
        self._task.setdefault(user_id, []).append(task)

    def get_tasks(self):
        return self._task

    def increment_id_task(self):
        self.id_task += 1

    def increment_id_user(self):
        self.user_id += 1

    def delete_task(self, user_id: int, task_id: int):
        for my_id, tasks in self._task.items():
            if my_id == user_id:
                for t in tasks:
                    if t.id == task_id:
                        self._task[user_id].remove(t)



    # User Method

    def add_user(self, user: UserInDb) -> UserInDb | None:
        for _, user_details in self._users.items():
            if user_details.username == user.username:
                return None
        user_id = self.user_id
        self._users[user_id] = user
        self.increment_id_user()
        return user

    def get_all_users(self):
        return self._users

    def check_user(self, user_id: int):
        if not user_id in self._users:
            return None
        return user_id

    def get_all_user_tasks(self, user_id: int) -> List[TaskInDb]:
        user_tasks = None
        for id_in_db, user_task in self._task.items():
            if id_in_db == user_id:
                user_tasks = user_task
                break
        return user_tasks

db_instance = DataBase()

# Endpoints

@app.get("/")
def index():
    return {
        "message": "Todo App"
    }

@app.post("/tasks", status_code = status.HTTP_201_CREATED)
def create_task(task: TaskCreate, user_id: int):
    if not task.title or not task.description:
        raise HTTPException(
            status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail = "All fields required"
        )
    user_id = db_instance.check_user(user_id)
    if not user_id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User does not exist"
        )

    new_task = TaskInDb(
        title = task.title,
        description = task.description,
        id = db_instance.id_task,
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow(),
        is_completed = False
    )
    db_instance.increment_id_task()
    db_instance.add_task(user_id = user_id, task = new_task)

    return {
        "success": True,
        "data": new_task,
        "message": "Task created successfully"
    }

@app.get("/tasks/by_id")
def get_user_tasks(id: int):
    user_id = db_instance.check_user(id)
    if not user_id:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User does not exist"
        )
    user_tasks = None
    for id_in_db, user_task in db_instance._task.items():
        if id_in_db == id:
            user_tasks = user_task
    return {
        "data": user_tasks,
        "message": "All User tasks retrieved successfully"
    }

@app.get("/tasks/by_username")
def get_task_with_username(username: str):
    for user_id, users in db_instance._users.items():
        if users.username == username:
            user_tasks = None
            for id_in_db, user_task in db_instance._task.items():
                if id_in_db == user_id:
                    user_tasks = user_task
            return {
                "success": True,
                "data": user_tasks,
                "message": "All user tasks retrieved succesfully"
            }
    else:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = "User does not exist"
        )
            


@app.patch("/tasks")
def partial_update(task: TaskUpdate):
    if not task.title and not task.description:
        raise HTTPException(
                status_code = status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail = "At least one field required"
                )
    # Check if user exists
    
    for user_id, tasks in db_instance._task.items():
        for t in tasks:
            if t.id == task.id:
                if task.title != None:
                    t.title = task.title
                if task.description != None:
                    t.description = task.description
                t.updated_at = datetime.utcnow()
                return {
                    "success": True,
                    "message": "Task updated successfully",
                    "data": t
                }

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Task not found"
    )
  
@app.get("/tasks/all")
def get_all_task():
    tasks = db_instance.get_tasks()
    return {
        "success": True,
        "data": tasks,
        "message": "All tasks retrieved successfully"
    }

@app.delete("/tasks", status_code=status.HTTP_204_NO_CONTENT)
def delete_user_task(user_id: int, task_id: int):
    if user_id:
        return db_instance.delete_task(user_id, task_id)
    else:
        raise HTTPException(
            status_code = status.HTTP_204_NO_CONTENT,
            detail = "User and task with ID not found"
        )
    
# User Endpoints

@app.post("/users")
def register_user(user: UserCreate):
    if not user.username or not user.password:
        raise HTTPException(
            status_code = status.HTTP_400_BAD_REQUEST,
            detail = "All fields required"
        )
    new_user = UserInDb(
        **user.model_dump(),
        created_at = datetime.utcnow(),
        updated_at = datetime.utcnow()
    )

    user = db_instance.add_user(new_user)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = "User already exists"
        )
    
    return {
        "success": True,
        "data": UserResponse(**user.model_dump(exclude_unset = True)),
        "message": "User created successfully"
    }

@app.get("/users")
def get_users():
    users = db_instance.get_all_users()
    return {
        "success": True,
        "data": users,
        "message": "All Users retrieved successfully"
    }


