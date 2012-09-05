"""drop_ticket_bundle_from_ticket_print_history

Revision ID: 2118ba6ee220
Revises: a2b7618aece
Create Date: 2012-09-05 17:59:07.723429

"""

# revision identifiers, used by Alembic.
revision = '2118ba6ee220'
down_revision = 'a2b7618aece'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_constraint('TicketPrintHistory_ibfk_4', 'TicketPrintHistory', type='foreignkey')
    op.drop_column('TicketPrintHistory', 'ticket_bundle_id')
    op.add_column('TicketPrintHistory', sa.Column('ticket_id', Identifier(), nullable=True))
    op.create_foreign_key('TicketPrintHistory_ibfk_4', 'TicketPrintHistory', 'Ticket', ['ticket_id'], ['id'])

def downgrade():
    op.drop_constraint('TicketPrintHistory_ibfk_4', 'TicketPrintHistory', type='foreignkey')
    op.drop_column('TicketPrintHistory', 'ticket_id')
    op.add_column('TicketPrintHistory', sa.Column('ticket_bundle_id', Identifier(), nullable=True))
    op.create_foreign_key('TicketPrintHistory_ibfk_4', 'TicketPrintHistory', 'TicketBundle', ['ticket_bundle_id'], ['id'])
