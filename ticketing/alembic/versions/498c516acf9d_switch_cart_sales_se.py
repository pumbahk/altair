"""switch cart sales_segment reference

Revision ID: 498c516acf9d
Revises: 47f92d43c86d
Create Date: 2013-01-27 18:33:01.500836

"""

# revision identifiers, used by Alembic.
revision = '498c516acf9d'
down_revision = '47f92d43c86d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE Cart DROP FOREIGN KEY Cart_ibfk_5")
    op.execute("ALTER TABLE Cart ADD FOREIGN KEY Cart_ibfk_5 (sales_segment_id) REFERENCES SalesSegment (id)")

def downgrade():
    op.execute("ALTER TABLE Cart DROP FOREIGN KEY Cart_ibfk_5")
    op.execute("ALTER TABLE Cart ADD FOREIGN KEY Cart_ibfk_5 (sales_segment_id) REFERENCES SalesSegmentGroup (id)")
