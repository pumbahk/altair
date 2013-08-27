"""ssg data migration

Revision ID: 53af2f49cb08
Revises: 4ecb439c0c44
Create Date: 2013-08-26 18:11:28.439336

"""

# revision identifiers, used by Alembic.
revision = '53af2f49cb08'
down_revision = '4ecb439c0c44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    sql = """\
    UPDATE SalesSegmentGroup
    SET start_day_prior_to_performance = 0,
    start_time = '00:00',
    end_day_prior_to_performance = 0,
    end_time = '00:00'
    """
    op.execute(sql)

def downgrade():
    pass
