from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Table,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.snowflake import next_snowflake_id


role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id", BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column(
        "permission_id",
        BigInteger,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", BigInteger, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )


class Permission(Base):
    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str] = mapped_column(String(255), default="")
    permissions: Mapped[list[Permission]] = relationship(secondary=role_permissions)


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    email: Mapped[str | None] = mapped_column(String(255), unique=True, index=True, nullable=True)
    full_name: Mapped[str] = mapped_column(String(120), default="")
    hashed_password: Mapped[str] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    roles: Mapped[list[Role]] = relationship(secondary=user_roles)


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    name: Mapped[str] = mapped_column(String(160), index=True)
    status: Mapped[str] = mapped_column(String(40), default="pending", index=True)
    progress: Mapped[int] = mapped_column(Integer, default=0)
    message: Mapped[str] = mapped_column(Text, default="")
    created_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )


class Asset(Base, TimestampMixin):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120), default="application/octet-stream")
    size: Mapped[int] = mapped_column(Integer, default=0)
    path: Mapped[str] = mapped_column(String(500))
    uploaded_by_id: Mapped[int | None] = mapped_column(
        BigInteger, ForeignKey("users.id"), nullable=True
    )


class Invoice(Base, TimestampMixin):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, index=True, default=next_snowflake_id
    )
    invoice_code: Mapped[str] = mapped_column(String(80), default="", index=True)
    invoice_number: Mapped[str] = mapped_column(String(80), default="", index=True)
    digital_invoice_number: Mapped[str] = mapped_column(String(80), default="", index=True)
    seller_tax_id: Mapped[str] = mapped_column(String(80), default="")
    seller_name: Mapped[str] = mapped_column(String(255), default="")
    buyer_tax_id: Mapped[str] = mapped_column(String(80), default="")
    buyer_name: Mapped[str] = mapped_column(String(255), default="")
    invoice_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    tax_classification_code: Mapped[str] = mapped_column(String(80), default="")
    specific_business_type: Mapped[str] = mapped_column(String(120), default="")
    taxable_item_name: Mapped[str] = mapped_column(String(500), default="")
    specification_model: Mapped[str] = mapped_column(String(255), default="")
    unit: Mapped[str] = mapped_column(String(40), default="")
    quantity: Mapped[Decimal | None] = mapped_column(Numeric(20, 6), nullable=True)
    unit_price: Mapped[Decimal | None] = mapped_column(Numeric(20, 15), nullable=True)
    amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    tax_rate: Mapped[str] = mapped_column(String(40), default="")
    tax_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(18, 2), nullable=True)
    invoice_source: Mapped[str] = mapped_column(String(120), default="")
    invoice_type: Mapped[str] = mapped_column(String(120), default="")
    invoice_status: Mapped[str] = mapped_column(String(80), default="")
    is_positive_invoice: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    invoice_risk_level: Mapped[str] = mapped_column(String(80), default="")
    issuer: Mapped[str] = mapped_column(String(120), default="")
    remark: Mapped[str] = mapped_column(Text, default="")
