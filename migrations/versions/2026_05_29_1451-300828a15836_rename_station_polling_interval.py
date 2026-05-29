"""rename station polling interval

Revision ID: 300828a15836
Revises: ad7ff15ca17e
Create Date: 2026-05-29 14:51:35.067583

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '300828a15836'
down_revision: Union[str, None] = 'ad7ff15ca17e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "stations",
        "polling_interval_seconds",
        new_column_name="polling_interval",
    )
    op.alter_column(
        "stations",
        "polling_interval",
        existing_type=sa.Integer(),
        type_=sa.Double(),
        postgresql_using="polling_interval::double precision / 60.0",
        existing_nullable=True,
    )
    op.execute(
        "UPDATE stations SET polling_interval = 0.5 WHERE polling_interval IS NULL"
    )
    op.alter_column(
        "stations",
        "polling_interval",
        existing_type=sa.Double(),
        nullable=False,
        server_default="0.5",
    )


def downgrade() -> None:
    op.alter_column(
        "stations",
        "polling_interval",
        existing_type=sa.Double(),
        type_=sa.Integer(),
        postgresql_using="ROUND(polling_interval * 60)::integer",
        existing_nullable=False,
        server_default=None,
    )
    op.alter_column(
        "stations",
        "polling_interval",
        new_column_name="polling_interval_seconds",
    )
