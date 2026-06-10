"""add username and invoices

Revision ID: b2a7f0d3c9e1
Revises: 4c5756561ca8
Create Date: 2026-06-09 00:00:00.000000
"""

import re

from alembic import op
import sqlalchemy as sa


revision = "b2a7f0d3c9e1"
down_revision = "4c5756561ca8"
branch_labels = None
depends_on = None


def _username_from_email(email: str, user_id: int, used: set[str]) -> str:
    base = email.split("@", 1)[0] if email else f"user_{user_id}"
    base = re.sub(r"[^0-9A-Za-z_.-]+", "_", base).strip("._-") or "user"
    candidate = base[:80]
    if candidate not in used:
        used.add(candidate)
        return candidate

    suffix = f"_{user_id}"
    candidate = f"{base[: 80 - len(suffix)]}{suffix}"
    used.add(candidate)
    return candidate


def upgrade() -> None:
    op.add_column("users", sa.Column("username", sa.String(length=80), nullable=True))

    bind = op.get_bind()
    rows = bind.execute(sa.text("SELECT id, email FROM users ORDER BY id")).mappings().all()
    used: set[str] = set()
    for row in rows:
        username = _username_from_email(str(row["email"] or ""), int(row["id"]), used)
        bind.execute(
            sa.text("UPDATE users SET username = :username WHERE id = :user_id"),
            {"username": username, "user_id": row["id"]},
        )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "username",
            existing_type=sa.String(length=80),
            nullable=False,
        )
    op.create_index(op.f("ix_users_username"), "users", ["username"], unique=True)

    op.create_table(
        "invoices",
        sa.Column(
            "id",
            sa.BigInteger(),
            autoincrement=False,
            nullable=False,
            comment="雪花ID",
        ),
        sa.Column(
            "invoice_code",
            sa.String(length=80),
            nullable=False,
            comment="发票代码",
        ),
        sa.Column(
            "invoice_number",
            sa.String(length=80),
            nullable=False,
            comment="发票号码",
        ),
        sa.Column(
            "digital_invoice_number",
            sa.String(length=80),
            nullable=False,
            comment="数电票号码",
        ),
        sa.Column(
            "seller_tax_id",
            sa.String(length=80),
            nullable=False,
            comment="销售方纳税人识别号",
        ),
        sa.Column(
            "seller_name",
            sa.String(length=255),
            nullable=False,
            comment="销售方名称",
        ),
        sa.Column(
            "buyer_tax_id",
            sa.String(length=80),
            nullable=False,
            comment="购买方纳税人识别号",
        ),
        sa.Column(
            "buyer_name",
            sa.String(length=255),
            nullable=False,
            comment="购买方名称",
        ),
        sa.Column("invoice_date", sa.Date(), nullable=True, comment="开票日期"),
        sa.Column(
            "tax_classification_code",
            sa.String(length=80),
            nullable=False,
            comment="税收分类编码",
        ),
        sa.Column(
            "specific_business_type",
            sa.String(length=120),
            nullable=False,
            comment="特定业务类型",
        ),
        sa.Column(
            "taxable_item_name",
            sa.String(length=500),
            nullable=False,
            comment="应税项目名称",
        ),
        sa.Column(
            "specification_model",
            sa.String(length=255),
            nullable=False,
            comment="规格型号",
        ),
        sa.Column("unit", sa.String(length=40), nullable=False, comment="单位"),
        sa.Column(
            "quantity",
            sa.Numeric(20, 6),
            nullable=True,
            comment="数量",
        ),
        sa.Column(
            "unit_price",
            sa.Numeric(20, 15),
            nullable=True,
            comment="单价",
        ),
        sa.Column(
            "amount",
            sa.Numeric(20, 2),
            nullable=True,
            comment="不含税金额",
        ),
        sa.Column(
            "tax_rate",
            sa.String(length=40),
            nullable=False,
            comment="税率",
        ),
        sa.Column(
            "tax_amount",
            sa.Numeric(18, 2),
            nullable=True,
            comment="税额",
        ),
        sa.Column(
            "total_amount",
            sa.Numeric(18, 2),
            nullable=True,
            comment="价税合计金额",
        ),
        sa.Column(
            "invoice_source",
            sa.String(length=120),
            nullable=False,
            comment="发票来源",
        ),
        sa.Column(
            "invoice_type",
            sa.String(length=120),
            nullable=False,
            comment="发票类型",
        ),
        sa.Column(
            "invoice_status",
            sa.String(length=80),
            nullable=False,
            comment="发票状态",
        ),
        sa.Column(
            "is_positive_invoice",
            sa.Boolean(),
            nullable=True,
            comment="是否为正数发票",
        ),
        sa.Column(
            "invoice_risk_level",
            sa.String(length=80),
            nullable=False,
            comment="发票风险等级",
        ),
        sa.Column(
            "issuer",
            sa.String(length=120),
            nullable=False,
            comment="开票人",
        ),
        sa.Column("remark", sa.Text(), nullable=False, comment="备注"),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
            comment="创建时间",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.func.now(),
            nullable=False,
            comment="更新时间",
        ),
        sa.PrimaryKeyConstraint("id"),
        comment="发票明细",
    )
    op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
    op.create_index(op.f("ix_invoices_invoice_code"), "invoices", ["invoice_code"], unique=False)
    op.create_index(
        op.f("ix_invoices_invoice_number"),
        "invoices",
        ["invoice_number"],
        unique=False,
    )
    op.create_index(
        op.f("ix_invoices_digital_invoice_number"),
        "invoices",
        ["digital_invoice_number"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_invoices_digital_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_number"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_invoice_code"), table_name="invoices")
    op.drop_index(op.f("ix_invoices_id"), table_name="invoices")
    op.drop_table("invoices")

    op.drop_index(op.f("ix_users_username"), table_name="users")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("username")
