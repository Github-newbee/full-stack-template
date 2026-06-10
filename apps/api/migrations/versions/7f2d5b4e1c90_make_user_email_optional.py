"""make user email optional

Revision ID: 7f2d5b4e1c90
Revises: b2a7f0d3c9e1
Create Date: 2026-06-10 14:30:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "7f2d5b4e1c90"
down_revision = "b2a7f0d3c9e1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=255),
            nullable=True,
        )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            "UPDATE users "
            "SET email = 'user_' || id || '@example.invalid' "
            "WHERE email IS NULL"
        )
    )

    with op.batch_alter_table("users") as batch_op:
        batch_op.alter_column(
            "email",
            existing_type=sa.String(length=255),
            nullable=False,
        )
