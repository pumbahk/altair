"""Add column SalesSegmentSetting for Point Allocation

Revision ID: 51dca1130748
Revises: 346464f0a12f
Create Date: 2018-10-05 14:22:15.479700

"""

# revision identifiers, used by Alembic.
revision = '51dca1130748'
down_revision = '346464f0a12f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentSetting',
                  sa.Column('enable_point_allocation', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('SalesSegmentSetting',
                  sa.Column('use_default_enable_point_allocation', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    op.drop_column('SalesSegmentSetting', 'enable_point_allocation')
    op.drop_column('SalesSegmentSetting', 'use_default_enable_point_allocation')
