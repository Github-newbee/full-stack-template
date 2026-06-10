from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.permissions import require_permission
from app.core.security import CurrentUser
from app.models import Task
from app.pagination import PageResponse
from app.schemas import TaskCreate, TaskRead
from app.tasks.service import TaskService


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
    result = TaskService(db).list_tasks(page=page, page_size=page_size)
    return PageResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


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
    return TaskService(db).create_task(payload, current_user)
