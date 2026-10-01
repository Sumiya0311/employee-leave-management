"""Rename employee type column

Revision ID: 45ad67558677
Revises: a081afc79ff2
"""

from alembic import op
import sqlalchemy as sa


revision = "45ad67558677"
down_revision = "a081afc79ff2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "employees",
        "employee_type",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        new_column_name="employment_type"
    )


def downgrade() -> None:
    op.alter_column(
        "employees",
        "employment_type",
        existing_type=sa.String(length=20),
        existing_nullable=False,
        new_column_name="employee_type"
    )