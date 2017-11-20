"""add display order to SalesSegmentGroup

Revision ID: 23db677af8c6
Revises: 2ddaa91d63d3
Create Date: 2017-11-16 20:28:24.046396

"""

# revision identifiers, used by Alembic.
revision = '23db677af8c6'
down_revision = '2ddaa91d63d3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroup', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default=text('1')))

def downgrade():
    op.drop_column('SalesSegmentGroup', 'display_order')
