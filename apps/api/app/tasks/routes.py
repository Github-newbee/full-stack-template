from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission
from app.core.security import CurrentUser
from app.models import Task
from app.pagination import PageResponse
from app.schemas import TaskCreate, TaskRead


router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get(
    "",
    response_model=PageResponse[TaskRead],
    dependencies=[Depends(require_permission("tasks.read"))],
)
def list_tasks(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageResponse[TaskRead]:
    total = db.scalar(select(func.count()).select_from(Task)) or 0
    tasks = db.scalars(
        select(Task).order_by(Task.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return PageResponse(items=list(tasks), total=total, page=page, page_size=page_size)


@router.post(
    "",
    response_model=TaskRead,
    dependencies=[Depends(require_permission("tasks.write"))],
)
def create_task(
    payload: TaskCreate,
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
) -> Task:
    task = Task(
        name=payload.name,
        message=payload.message,
        status="queued",
        created_by_id=current_user.id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
