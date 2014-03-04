"""add column SalesSegmentGroupSetting.display_seat_no

Revision ID: 3e2e37602d0b
Revises: 15f7cc655ec3
Create Date: 2014-03-04 10:19:05.268721

"""

# revision identifiers, used by Alembic.
revision = '3e2e37602d0b'
down_revision = '15f7cc655ec3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegmentGroupSetting', sa.Column(u'display_seat_no', sa.Boolean, default=True, server_default='1'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'display_seat_no', sa.Boolean, default=True, server_default='1'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'use_default_display_seat_no', sa.Boolean))
    op.execute(u'UPDATE SalesSegmentSetting SET use_default_display_seat_no = 1')

def downgrade():
    op.drop_column(u'SalesSegmentSetting', u'use_default_display_seat_no')
    op.drop_column(u'SalesSegmentSetting', u'display_seat_no')
    op.drop_column(u'SalesSegmentGroupSetting', u'display_seat_no')
