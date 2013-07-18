"""add column reporting on SalesSegment

Revision ID: 462e944c1c46
Revises: 1e07ec9500e3
Create Date: 2013-07-18 15:11:42.983486

"""

# revision identifiers, used by Alembic.
revision = '462e944c1c46'
down_revision = '1e07ec9500e3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegmentGroup', sa.Column('reporting', sa.Boolean(), nullable=False, default=True, server_default=text('1')))
    op.add_column(u'SalesSegment', sa.Column('reporting', sa.Boolean(), nullable=False, default=True, server_default=text('1')))
    op.execute("UPDATE `SalesSegmentGroup` SET reporting=0 WHERE public = 0")
    op.execute("UPDATE `SalesSegment` SET reporting=0 WHERE public = 0")

def downgrade():
    op.drop_column(u'SalesSegment', 'reporting')
    op.drop_column(u'SalesSegmentGroup', 'reporting')
