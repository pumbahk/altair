"""TicketPrintQueueEntry.masked_at

Revision ID: 1b8b46eff15
Revises: 462e944c1c46
Create Date: 2013-07-26 19:33:53.217558

"""

# revision identifiers, used by Alembic.
revision = '1b8b46eff15'
down_revision = '462e944c1c46'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('TicketPrintQueueEntry', sa.Column('masked_at', sa.TIMESTAMP(), nullable=True))

def downgrade():
    op.drop_column('TicketPrintQueueEntry', 'masked_at')
