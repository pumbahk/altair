"""rename column Lot

Revision ID: 333d0bcd2f83
Revises: 4316a6bc8845
Create Date: 2013-01-24 18:03:38.130174

"""

# revision identifiers, used by Alembic.
revision = '333d0bcd2f83'
down_revision = '4316a6bc8845'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""\
ALTER TABLE Lot DROP FOREIGN KEY Lot_ibfk_2;
ALTER TABLE Lot CHANGE COLUMN sales_segment_id sales_segment_group_id BIGINT;
ALTER TABLE Lot ADD CONSTRAINT Lot_ibfk_2 FOREIGN KEY (sales_segment_group_id) REFERENCES SalesSegmentGroup (id);
""")

def downgrade():
    op.execute("""\
ALTER TABLE Lot DROP FOREIGN KEY Lot_ibfk_2;
ALTER TABLE Lot CHANGE COLUMN sales_segment_group_id sales_segment_id BIGINT;
ALTER TABLE Lot ADD CONSTRAINT Lot_ibfk_2 FOREIGN KEY (sales_segment_id) REFERENCES SalesSegmentGroup (id);
""")
