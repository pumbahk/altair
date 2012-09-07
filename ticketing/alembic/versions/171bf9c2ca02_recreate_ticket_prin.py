"""recreate_ticket_print_queue

Revision ID: 171bf9c2ca02
Revises: 14fb6e01812b
Create Date: 2012-09-02 16:08:45.445165

"""

# revision identifiers, used by Alembic.
revision = '171bf9c2ca02'
down_revision = '14fb6e01812b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects import mysql

Identifier = sa.BigInteger

def upgrade():
    op.drop_table('TicketPrintQueue')
    op.create_table('TicketPrintQueueEntry',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('ordered_product_item_id', Identifier(), nullable=True),
        sa.Column('seat_id', Identifier(), nullable=True),
        sa.Column('ticket_id', Identifier(), nullable=False),
        sa.Column('summary', sa.Unicode(255), nullable=False, default=u''),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('processed_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ticketprintqueueentry_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], 'ticketprintqueueentry_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'ticketprintqueueentry_ibfk_3', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_id'], ['Ticket.id'], 'ticketprintqueueentry_ibfk_4', ondelete='CASCADE')
        )

def downgrade():
    op.drop_constraint('ticketprintqueueentry_ibfk_1', 'TicketPrintQueueEntry', type='foreignkey')
    op.drop_constraint('ticketprintqueueentry_ibfk_2', 'TicketPrintQueueEntry', type='foreignkey')
    op.drop_constraint('ticketprintqueueentry_ibfk_3', 'TicketPrintQueueEntry', type='foreignkey')
    op.drop_constraint('ticketprintqueueentry_ibfk_4', 'TicketPrintQueueEntry', type='foreignkey')
    op.drop_table('TicketPrintQueueEntry')
    op.create_table('TicketPrintQueue',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ticketprintqueue_ibfk_1', ondelete='CASCADE'),
        )
