"""add_ticket_type

Revision ID: 53a1eba253dd
Revises: a185b0fe658
Create Date: 2013-05-31 14:33:14.582615

"""

# revision identifiers, used by Alembic.
revision = '53a1eba253dd'
down_revision = 'a185b0fe658'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'TicketType',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('display_name', sa.Unicode(255), nullable=True),
        sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default=text('1')),
        sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default=text('1')),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('stock_type_id', Identifier(), nullable=False),
        sa.Column('stock_holder_id', Identifier(), nullable=False),
        sa.Column('ticket_bundle_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'TicketType_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], 'TicketType_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['stock_holder_id'], ['StockHolder.id'], 'TicketType_ibfk_3', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['ticket_bundle_id'], ['TicketBundle.id'], 'TicketType_ibfk_4', ondelete='CASCADE')
        )
    op.add_column('Product', sa.Column('ticket_type_id', Identifier(), nullable=True))
    op.create_foreign_key('Product_ibfk_5', 'Product', 'TicketType', ['ticket_type_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('Product_ibfk_5', 'Product', type_='foreignkey')
    op.drop_column('Product', 'ticket_type_id')
    op.drop_table('TicketType')
