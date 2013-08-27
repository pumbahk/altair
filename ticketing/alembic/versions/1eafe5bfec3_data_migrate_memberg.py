"""data migrate MemberGroup_SalesSegmentGroup

Revision ID: 1eafe5bfec3
Revises: 38a4c226c27c
Create Date: 2013-08-09 13:39:35.858689

"""

# revision identifiers, used by Alembic.
revision = '1eafe5bfec3'
down_revision = '38a4c226c27c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    sql = """\
    INSERT INTO MemberGroup_SalesSegmentGroup
    (
    membergroup_id,
    sales_segment_group_id
    )
    SELECT
    membergroup_id,
    sales_segment_group_id
    FROM MemberGroup_SalesSegment

"""
    op.execute(sql)

def downgrade():
    pass
