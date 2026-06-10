from sqlalchemy.orm import Session

from app.models import Task, User
from app.pagination import PageResult
from app.schemas import TaskCreate
from app.tasks.repository import TaskRepository


class TaskService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.tasks = TaskRepository(db)

    def list_tasks(self, *, page: int, page_size: int) -> PageResult[Task]:
        total = self.tasks.count()
        tasks = self.tasks.list_page(offset=(page - 1) * page_size, limit=page_size)
        return PageResult(items=tasks, total=total, page=page, page_size=page_size)

    def create_task(self, payload: TaskCreate, current_user: User) -> Task:
        task = Task(
            name=payload.name,
            message=payload.message,
            status="queued",
            created_by_id=current_user.id,
        )
        self.tasks.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
