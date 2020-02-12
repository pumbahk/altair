"""add usage valid date for ticket hub order tickets table

Revision ID: c46ba3887fb
Revises: 1d494fd22d5b
Create Date: 2020-02-10 12:13:14.409620

"""

# revision identifiers, used by Alembic.
revision = 'c46ba3887fb'
down_revision = '1d494fd22d5b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('TicketHubOrderedTicket', sa.Column('usage_valid_start_date', sa.DateTime(), nullable=True))
    op.add_column('TicketHubOrderedTicket', sa.Column('usage_valid_end_date', sa.DateTime(), nullable=True))


def downgrade():
    op.drop_column('TicketHubOrderedTicket', 'usage_valid_start_date')
    op.drop_column('TicketHubOrderedTicket', 'usage_valid_end_date')
