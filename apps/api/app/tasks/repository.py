from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Task


class TaskRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Task)) or 0

    def list_page(self, *, offset: int, limit: int) -> list[Task]:
        return list(
            self.db.scalars(select(Task).order_by(Task.id.desc()).offset(offset).limit(limit)).all()
        )

    def add(self, task: Task) -> None:
        self.db.add(task)
