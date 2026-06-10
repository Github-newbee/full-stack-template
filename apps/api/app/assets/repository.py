from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Asset


class AssetRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def count(self) -> int:
        return self.db.scalar(select(func.count()).select_from(Asset)) or 0

    def list_page(self, *, offset: int, limit: int) -> list[Asset]:
        return list(
            self.db.scalars(
                select(Asset).order_by(Asset.id.desc()).offset(offset).limit(limit)
            ).all()
        )

    def get(self, asset_id: int) -> Asset | None:
        return self.db.get(Asset, asset_id)

    def add(self, asset: Asset) -> None:
        self.db.add(asset)
