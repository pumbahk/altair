"""empty message

Revision ID: dc06c3ebfa5
Revises: 330fbffaf765
Create Date: 2014-04-01 16:20:01.440520

"""

# revision identifiers, used by Alembic.
revision = 'dc06c3ebfa5'
down_revision = '330fbffaf765'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegmentGroupSetting', sa.Column(u'sales_counter_selectable', sa.Boolean, default=True, server_default='1'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'sales_counter_selectable', sa.Boolean, default=True, server_default='1'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'use_default_sales_counter_selectable', sa.Boolean))
    op.execute(u'UPDATE SalesSegmentSetting SET use_default_sales_counter_selectable = 1')

def downgrade():
    op.drop_column(u'SalesSegmentGroupSetting', u'sales_counter_selectable')
    op.drop_column(u'SalesSegmentSetting', u'sales_counter_selectable')
    op.drop_column(u'SalesSegmentSetting', u'use_default_sales_counter_selectable')
