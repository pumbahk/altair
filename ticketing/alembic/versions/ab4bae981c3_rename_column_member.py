"""rename column MemberGroup_SalesSegment

Revision ID: ab4bae981c3
Revises: 398b8a0974eb
Create Date: 2013-01-24 18:02:35.242137

"""

# revision identifiers, used by Alembic.
revision = 'ab4bae981c3'
down_revision = '4a85433c818a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""\
ALTER TABLE MemberGroup_SalesSegment DROP FOREIGN KEY MemberGroup_SalesSegment_ibfk_2;
ALTER TABLE MemberGroup_SalesSegment CHANGE COLUMN sales_segment_id sales_segment_group_id BIGINT;
ALTER TABLE MemberGroup_SalesSegment ADD CONSTRAINT MemberGroup_SalesSegment_ibfk_2 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id);
""")

def downgrade():
    op.execute("""\
ALTER TABLE MemberGroup_SalesSegment DROP FOREIGN KEY MemberGroup_SalesSegment_ibfk_2;
ALTER TABLE MemberGroup_SalesSegment CHANGE COLUMN sales_segment_group_id sales_segment_id BIGINT;
ALTER TABLE MemberGroup_SalesSegment ADD CONSTRAINT MemberGroup_SalesSegment_ibfk_2 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegmentGroup (id);
""")
