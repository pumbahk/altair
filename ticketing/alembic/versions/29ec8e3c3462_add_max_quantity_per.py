"""add_max_quantity_per_user_to_setting_tables

Revision ID: 29ec8e3c3462
Revises: b58b20bfeae
Create Date: 2014-01-28 10:23:55.655140

"""

# revision identifiers, used by Alembic.
revision = '29ec8e3c3462'
down_revision = 'b58b20bfeae'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting', sa.Column('max_quantity_per_user', sa.Integer, default=None))
    op.add_column('PerformanceSetting', sa.Column('max_quantity_per_user', sa.Integer, default=None))
    op.add_column('SalesSegmentSetting', sa.Column('max_quantity_per_user', sa.Integer, default=None))
    op.add_column('SalesSegmentSetting', sa.Column('use_default_max_quantity_per_user', sa.Boolean, default=None))
    op.add_column('SalesSegmentGroupSetting', sa.Column('max_quantity_per_user', sa.Integer, default=None))

def downgrade():
    op.drop_column('EventSetting', 'max_quantity_per_user')
    op.drop_column('PerformanceSetting', 'max_quantity_per_user')
    op.drop_column('SalesSegmentSetting', 'max_quantity_per_user')
    op.drop_column('SalesSegmentSetting', 'use_default_max_quantity_per_user')
    op.drop_column('SalesSegmentGroupSetting', 'max_quantity_per_user')
