"""add tickethub ticket columns

Revision ID: d06c6c49628
Revises: e70924e0642
Create Date: 2019-11-29 01:13:08.409741

"""

# revision identifiers, used by Alembic.
revision = 'd06c6c49628'
down_revision = 'e70924e0642'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'TicketHubOrderedTicket', sa.Column(u'display_ticket_id', sa.String(length=30), nullable=False))

def downgrade():
    op.drop_column(u'TicketHubOrderedTicket', u'display_ticket_id')
