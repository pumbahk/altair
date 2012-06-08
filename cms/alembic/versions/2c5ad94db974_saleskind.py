"""saleskind

Revision ID: 2c5ad94db974
Revises: 1d86fe95e558
Create Date: 2012-06-08 10:16:28.032611

"""

# revision identifiers, used by Alembic.
revision = '2c5ad94db974'
down_revision = '1d86fe95e558'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column("sale", "name", type_=sa.Unicode(length=255), existing_type=sa.String(length=255))

def downgrade():
    op.alter_column("sale", "name", existing_type=sa.Unicode(length=255), type_=sa.String(length=255))


