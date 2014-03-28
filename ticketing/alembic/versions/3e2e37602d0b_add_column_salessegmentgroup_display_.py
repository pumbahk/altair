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
    op.execute(u'UPDATE SalesSegmentSetting se, SalesSegment ss SET se.display_seat_no = ss.seat_choice, se.use_default_display_seat_no = ss.use_default_seat_choice WHERE se.sales_segment_id = ss.id')
    op.execute(u'UPDATE SalesSegmentGroupSetting se, SalesSegmentGroup ssg SET se.display_seat_no = ssg.seat_choice WHERE se.sales_segment_group_id = ssg.id')
    op.execute(u'UPDATE SalesSegmentSetting se, SalesSegment ss SET se.display_seat_no = 1 WHERE se.sales_segment_id = ss.id AND ss.organization_id = 24')
    op.execute(u'UPDATE SalesSegmentGroupSetting se, SalesSegmentGroup ssg SET se.display_seat_no = 1 WHERE se.sales_segment_group_id = ssg.id AND ssg.organization_id = 24')

def downgrade():
    op.drop_column(u'SalesSegmentSetting', u'use_default_display_seat_no')
    op.drop_column(u'SalesSegmentSetting', u'display_seat_no')
    op.drop_column(u'SalesSegmentGroupSetting', u'display_seat_no')
