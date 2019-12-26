"""add ResaleRequest to stock_count_at

Revision ID: 3cbf08c390d9
Revises: 52520f5bf901
Create Date: 2019-12-03 16:33:51.895857

"""

# revision identifiers, used by Alembic.
revision = '3cbf08c390d9'
down_revision = '52520f5bf901'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ResaleRequest', sa.Column('stock_count_at', sa.TIMESTAMP(), nullable=True))

def downgrade():
    op.drop_column('ResaleRequest', 'stock_count_at')
