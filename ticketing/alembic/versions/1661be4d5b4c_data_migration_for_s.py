# -*- coding:utf-8 -*-
"""data migration for SalesSegment organization event

Revision ID: 1661be4d5b4c
Revises: 1fe48fdf7cc0
Create Date: 2013-08-08 15:42:44.266517

"""

# revision identifiers, used by Alembic.
revision = '1661be4d5b4c'
down_revision = '1fe48fdf7cc0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    sql = """\
UPDATE SalesSegment
JOIN SalesSegmentGroup
ON SalesSegment.sales_segment_group_id = SalesSegmentGroup.id
JOIN Event
ON SalesSegmentGroup.event_id = Event.id
SET 
 SalesSegment.event_id = SalesSegmentGroup.event_id,
 SalesSegment.organization_id = Event.organization_id
"""
    op.execute(sql)

def downgrade():
    sql = """\
UPDATE SalesSegment
SET 
 SalesSegment.event_id = NULL,
 SalesSegment.organization_id = NULL
"""
    op.execute(sql)

