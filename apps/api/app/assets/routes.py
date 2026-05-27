from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db
from app.core.permissions import require_permission
from app.core.security import CurrentUser
from app.core.snowflake import parse_snowflake_id
from app.models import Asset
from app.pagination import PageResponse
from app.schemas import AssetRead


router = APIRouter(prefix="/assets", tags=["assets"])


def parse_request_id(value: str) -> int:
    try:
        return parse_snowflake_id(value)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail="Invalid snowflake id") from exc


@router.get(
    "",
    response_model=PageResponse[AssetRead],
    dependencies=[Depends(require_permission("assets.read"))],
)
def list_assets(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> PageResponse[AssetRead]:
    total = db.scalar(select(func.count()).select_from(Asset)) or 0
    assets = db.scalars(
        select(Asset).order_by(Asset.id.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return PageResponse(items=list(assets), total=total, page=page, page_size=page_size)


@router.post(
    "",
    response_model=AssetRead,
    dependencies=[Depends(require_permission("assets.write"))],
)
async def upload_asset(
    current_user: CurrentUser,
    db: Annotated[Session, Depends(get_db)],
    file: UploadFile = File(...),
) -> Asset:
    settings = get_settings()
    data = await file.read()
    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(data) > max_bytes:
        raise HTTPException(status_code=413, detail="File is too large")

    suffix = Path(file.filename or "asset").suffix
    stored_name = f"{uuid4().hex}{suffix}"
    path = settings.storage_dir / stored_name
    path.write_bytes(data)

    asset = Asset(
        filename=file.filename or stored_name,
        content_type=file.content_type or "application/octet-stream",
        size=len(data),
        path=str(path),
        uploaded_by_id=current_user.id,
    )
    db.add(asset)
    db.commit()
    db.refresh(asset)
    return asset


@router.get(
    "/{asset_id}/download",
    dependencies=[Depends(require_permission("assets.read"))],
)
def download_asset(asset_id: str, db: Annotated[Session, Depends(get_db)]) -> FileResponse:
    asset = db.get(Asset, parse_request_id(asset_id))
    if asset is None or not Path(asset.path).exists():
        raise HTTPException(status_code=404, detail="Asset not found")
    return FileResponse(asset.path, media_type=asset.content_type, filename=asset.filename)
