"""rename column Product

Revision ID: 2d71b810a558
Revises: ab4bae981c3
Create Date: 2013-01-24 18:02:56.619270

"""

# revision identifiers, used by Alembic.
revision = '2d71b810a558'
down_revision = 'ab4bae981c3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""\
ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_1;
ALTER TABLE Product CHANGE COLUMN sales_segment_id sales_segment_group_id BIGINT;
ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id);
""")

def downgrade():
    op.execute("""\
ALTER TABLE Product DROP FOREIGN KEY Product_ibfk_1;
ALTER TABLE Product CHANGE COLUMN sales_segment_group_id sales_segment_id BIGINT;
ALTER TABLE Product ADD CONSTRAINT Product_ibfk_1 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegmentGroup (id);
""")
