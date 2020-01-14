"""Add attribute columns to StockType.

Revision ID: 1591106d2def
Revises: 168193aead8d
Create Date: 2019-11-27 19:24:20.456240

"""

# revision identifiers, used by Alembic.
revision = '1591106d2def'
down_revision = '168193aead8d'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('StockType', sa.Column('attribute', sa.String(255), nullable=True))


def downgrade():
    op.drop_column('StockType', 'attribute')
