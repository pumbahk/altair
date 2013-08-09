"""data migrate MemberGroup_SalesSegment

Revision ID: 571cbcc79a61
Revises: 1eafe5bfec3
Create Date: 2013-08-09 14:00:56.014220

"""

# revision identifiers, used by Alembic.
revision = '571cbcc79a61'
down_revision = '1eafe5bfec3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():

    sql1 = """\
INSERT INTO MemberGroup_SalesSegment
(
sales_segment_id,
membergroup_id
)
SELECT SalesSegment.id AS sales_segment_id, MemberGroup_SalesSegmentGroup.membergroup_id
FROM SalesSegment
JOIN SalesSegmentGroup
ON SalesSegmentGroup.id = SalesSegment.sales_segment_group_id
JOIN MemberGroup_SalesSegmentGroup
ON SalesSegmentGroup.id = MemberGroup_SalesSegmentGroup.sales_segment_group_id
"""
    op.execute(sql1)

    sql2 = """\
DELETE FROM MemberGroup_SalesSegment
WHERE sales_segment_id IS NULL
"""
    op.execute(sql2)

def downgrade():
    sql1 = """\
DELETE FROM MemberGroup_SalesSegment
WHERE sales_segment_id IS NOT NULL
"""
    op.execute(sql1)

    sql2 = """\
INSERT INTO MemberGroup_SalesSegment
(
sales_segment_group_id,
membergroup_id
)
SELECT SalesSegmentGroup.id AS sales_segment_group_id, MemberGroup_SalesSegmentGroup.membergroup_id
FROM SalesSegmentGroup
JOIN MemberGroup_SalesSegmentGroup
ON SalesSegmentGroup.id = MemberGroup_SalesSegmentGroup.sales_segment_group_id
"""
    op.execute(sql2)
