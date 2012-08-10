"""recreate_ticket_tables

Revision ID: 4b3401617faa
Revises: 38dd1fa48f1f
Create Date: 2012-08-10 16:06:41.335359

"""

# revision identifiers, used by Alembic.
revision = '4b3401617faa'
down_revision = '38dd1fa48f1f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def create_old_ticket_tables():
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

def create_ticket_tables():
    op.create_table('TicketFormat',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('delivery_method_id', Identifier(), nullable=True),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'TicketFormat_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['delivery_method_id'], ['DeliveryMethod.id'], 'TicketFormat_ibfk_2', ondelete='CASCADE')
        )
    op.create_table('Ticket',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(length=255), nullable=False),
        sa.Column('data', sa.String(length=65536), nullable=False, default=''),
        sa.Column('ticket_format_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'Ticket_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'Ticket_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_format_id'], ['TicketFormat.id'], 'Ticket_ibfk_3', ondelete='CASCADE')
        )
    op.create_table('TicketBundle',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('name', sa.Unicode(255), default=u'', nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'TicketBundle_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'TicketBundle_ibfk_2')
        )
    op.create_table('TicketBundleAttribute',
        sa.Column('ticket_bundle_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('value', sa.String(1023)),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['ticket_bundle_id'], ['TicketBundle.id'], 'TicketBundleAttribute_ibfk_1', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('ticket_bundle_id', 'name')
        )
    op.create_table('Ticket_TicketBundle',
        sa.Column('ticket_bundle_id', Identifier(), nullable=False),
        sa.Column('ticket_id', Identifier(), nullable=False),
        sa.ForeignKeyConstraint(['ticket_bundle_id'], ['TicketBundle.id'], 'Ticket_TicketBundle_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_id'], ['Ticket.id'], 'Ticket_TicketBundle_ibfk_2', ondelete='CASCADE')
        )
    op.create_table('TicketPrintHistory',
        sa.Column('id', Identifier(), autoincrement=True, nullable=False),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('ordered_product_item_id', Identifier(), nullable=True),
        sa.Column('seat_id', Identifier(), nullable=True),
        sa.Column('ticket_bundle_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'TicketPrintHistory_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], 'TicketPrintHistory_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'TicketPrintHistory_ibfk_3', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_bundle_id'], ['TicketBundle.id'], 'TicketPrintHistory_ibfk_4', ondelete='CASCADE')
        )

def upgrade():
    op.drop_table('TicketPrintHistory')
    op.drop_table('TicketAttribute')
    op.drop_table('Ticket')
    op.drop_table('TicketTemplate')
    create_ticket_tables()
    op.add_column('ProductItem', sa.Column('ticket_bundle_id', Identifier(), nullable=True))
    op.create_foreign_key('ProductItem_ibfk_4', 'ProductItem', 'TicketBundle', ['ticket_bundle_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('ProductItem_ibfk_4', 'ProductItem', 'foreignkey')
    op.drop_column('ProductItem', 'ticket_bundle_id')
    op.drop_table('TicketPrintHistory')
    op.drop_table('TicketBundleAttribute')
    op.drop_table('Ticket_TicketBundle')
    op.drop_table('TicketBundle')
    op.drop_table('Ticket')
    op.drop_table('TicketFormat')
    create_old_ticket_tables()
