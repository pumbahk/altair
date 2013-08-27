"""SaelsSegments.[start|end]_day_prior_to

Revision ID: 4ecb439c0c44
Revises: b0fd98b49bf
Create Date: 2013-08-26 11:29:57.767670

"""

# revision identifiers, used by Alembic.
revision = '4ecb439c0c44'
down_revision = 'b0fd98b49bf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegmentGroup", 
                  sa.Column('start_day_prior_to_performance', sa.Integer))
    op.add_column("SalesSegmentGroup",
                  sa.Column("start_time", sa.Time))
    op.add_column("SalesSegmentGroup",
                  sa.Column("end_day_prior_to_performance", sa.Integer))
    op.add_column("SalesSegmentGroup",
                  sa.Column("end_time", sa.Time))


def downgrade():
    op.drop_column("SalesSegmentGroup", 'start_day_prior_to_performance')
    op.drop_column("SalesSegmentGroup", "start_time")
    op.drop_column("SalesSegmentGroup", "end_day_prior_to_performance")
    op.drop_column("SalesSegmentGroup", "end_time")

