from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.assets.service import AssetService
from app.core.database import get_db
from app.core.errors import ServiceError, to_http_exception
from app.core.permissions import require_permission
from app.core.request_ids import parse_request_id
from app.core.security import CurrentUser
from app.models import Asset
from app.pagination import PageResponse
from app.schemas import AssetRead


router = APIRouter(prefix="/assets", tags=["assets"])


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
    result = AssetService(db).list_assets(page=page, page_size=page_size)
    return PageResponse(
        items=result.items,
        total=result.total,
        page=result.page,
        page_size=result.page_size,
    )


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
    data = await file.read()
    try:
        return AssetService(db).upload_asset(
            current_user=current_user,
            filename=file.filename,
            content_type=file.content_type,
            data=data,
        )
    except ServiceError as exc:
        raise to_http_exception(exc) from exc


@router.get(
    "/{asset_id}/download",
    dependencies=[Depends(require_permission("assets.read"))],
)
def download_asset(asset_id: str, db: Annotated[Session, Depends(get_db)]) -> FileResponse:
    try:
        asset = AssetService(db).get_download_asset(parse_request_id(asset_id))
    except ServiceError as exc:
        raise to_http_exception(exc) from exc
    return FileResponse(asset.path, media_type=asset.content_type, filename=asset.filename)
