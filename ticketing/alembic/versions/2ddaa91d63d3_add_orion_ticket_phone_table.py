"""add orion_ticket_phone table

Revision ID: 2ddaa91d63d3
Revises: 7d530c296b4
Create Date: 2017-10-24 11:41:24.620419

"""

# revision identifiers, used by Alembic.
revision = '2ddaa91d63d3'
down_revision = '7d530c296b4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('OrionTicketPhone',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('user_id', Identifier(), nullable=True),
                    sa.Column('order_no', sa.String(20), nullable=False, server_default=''),
                    sa.Column('entry_no', sa.String(20), nullable=False, server_default=''),
                    sa.Column('phones', sa.String(length=255), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'OrionTicketPhone_ibfk_1'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_unique_constraint('uix_OrionTicketPhone_order_no_entry_no', 'OrionTicketPhone',
                                ['order_no', 'entry_no'])
    op.create_index('idx_OrionTicketPhone_order_no', 'OrionTicketPhone', ['order_no'])
    op.create_index('idx_OrionTicketPhone_entry_no', 'OrionTicketPhone', ['entry_no'])

def downgrade():
    op.drop_index('idx_OrionTicketPhone_entry_no', 'OrionTicketPhone')
    op.drop_index('idx_OrionTicketPhone_order_no', 'OrionTicketPhone')
    op.drop_constraint('uix_OrionTicketPhone_order_no_entry_no', 'OrionTicketPhone', type_='unique')
    op.drop_table('OrionTicketPhone')