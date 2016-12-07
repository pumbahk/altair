"""alter table SalesSegmentGroup, SalesSegment add column stock_holder_id

Revision ID: 3d11d457ae32
Revises: 8d3e9ae2ecf
Create Date: 2016-12-02 11:39:45.194868

"""

# revision identifiers, used by Alembic.
revision = '3d11d457ae32'
down_revision = '8d3e9ae2ecf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroup', sa.Column('stock_holder_id', sa.Integer, default=None))
    op.add_column('SalesSegment', sa.Column('stock_holder_id', sa.Boolean))
    op.add_column('SalesSegment', sa.Column('use_default_stock_holder_id', sa.Boolean))


def downgrade():
    op.drop_column('SalesSegmentGroup', 'stock_holder_id')
    op.drop_column('SalesSegment', 'stock_holder_id')
    op.drop_column('SalesSegment', 'use_default_stock_holder_id')
