from pathlib import Path
from uuid import uuid4

from sqlalchemy.orm import Session

from app.assets.repository import AssetRepository
from app.core.config import get_settings
from app.core.errors import NotFoundError, PayloadTooLargeError
from app.models import Asset, User
from app.pagination import PageResult


class AssetService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.assets = AssetRepository(db)

    def list_assets(self, *, page: int, page_size: int) -> PageResult[Asset]:
        total = self.assets.count()
        assets = self.assets.list_page(offset=(page - 1) * page_size, limit=page_size)
        return PageResult(items=assets, total=total, page=page, page_size=page_size)

    def upload_asset(
        self,
        *,
        current_user: User,
        filename: str | None,
        content_type: str | None,
        data: bytes,
    ) -> Asset:
        settings = get_settings()
        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(data) > max_bytes:
            raise PayloadTooLargeError("File is too large")

        suffix = Path(filename or "asset").suffix
        stored_name = f"{uuid4().hex}{suffix}"
        path = settings.storage_dir / stored_name
        path.write_bytes(data)

        asset = Asset(
            filename=filename or stored_name,
            content_type=content_type or "application/octet-stream",
            size=len(data),
            path=str(path),
            uploaded_by_id=current_user.id,
        )
        self.assets.add(asset)
        self.db.commit()
        self.db.refresh(asset)
        return asset

    def get_download_asset(self, asset_id: int) -> Asset:
        asset = self.assets.get(asset_id)
        if asset is None or not Path(asset.path).exists():
            raise NotFoundError("Asset not found")
        return asset
