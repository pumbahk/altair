"""add_ticket_tables

Revision ID: 297a875d82ea
Revises: 7fd74bf0044
Create Date: 2012-08-02 15:54:58.027448

"""

# revision identifiers, used by Alembic.
revision = '297a875d82ea'
down_revision = '50e50f325afb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def create_ticket_tables():
    op.create_table('TicketTemplate',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'tickettemplate_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'tickettemplate_ibfk_2', ondelete='CASCADE')
        )
    op.create_table('Ticket',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('template_id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(255), default=u'', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'ticket_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['template_id'], ['TicketTemplate.id'], 'ticket_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ticket_ibfk_3')
        )
    op.create_table('TicketAttribute',
        sa.Column('ticket_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('value', sa.String(1023)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_id'], ['Ticket.id'], 'ticketattribute_ibfk_1', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('ticket_id', 'name')
        )
    op.create_table('TicketPrintHistory',
        sa.Column('id', Identifier(), autoincrement=True, nullable=False),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('ordered_product_item_id', Identifier(), nullable=True),
        sa.Column('seat_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ticketprinthistory_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], 'ticketprinthistory_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'ticketprinthistory_ibfk_3', ondelete='CASCADE')
        )

def upgrade():
    create_ticket_tables()

def downgrade():
    op.drop_table('TicketPrintHistory')
    op.drop_table('TicketAttribute')
    op.drop_table('Ticket')
    op.drop_table('TicketTemplate')
