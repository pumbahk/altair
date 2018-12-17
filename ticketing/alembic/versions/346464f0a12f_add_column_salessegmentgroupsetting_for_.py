"""Add column SalesSegmentGroupSetting for Point Allocation

Revision ID: 346464f0a12f
Revises: 367c56cd18b3
Create Date: 2018-10-05 14:16:50.242661

"""

# revision identifiers, used by Alembic.
revision = '346464f0a12f'
down_revision = '367c56cd18b3'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroupSetting',
                  sa.Column('enable_point_allocation', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('SalesSegmentGroupSetting', 'enable_point_allocation')
