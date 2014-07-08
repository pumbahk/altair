"""altair table SejRefundTicket add columns

Revision ID: 2a47a06a6a4b
Revises: 12b52292a9c0
Create Date: 2014-07-04 13:56:13.853769

"""

# revision identifiers, used by Alembic.
revision = '2a47a06a6a4b'
down_revision = '2343faa27795'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SejRefundTicket', sa.Column(u'refunded_at', sa.DateTime, nullable=True))
    op.add_column(u'SejRefundTicket', sa.Column(u'status', sa.Integer))

def downgrade():
    op.drop_column(u'SejRefundTicket', u'refunded_at')
    op.drop_column(u'SejRefundTicket', u'status')
