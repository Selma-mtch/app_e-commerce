"""add product image_url

Revision ID: b3c9a4d6e7f1
Revises: 28cce2b0ab47
Create Date: 2025-12-19 22:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c9a4d6e7f1'
down_revision: Union[str, None] = '28cce2b0ab47'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add image_url column to products
    op.add_column('products', sa.Column('image_url', sa.String(length=1024), nullable=True))


def downgrade() -> None:
    # Remove image_url column
    op.drop_column('products', 'image_url')
