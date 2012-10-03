"""add_order_id_to_ticketprinthistory

Revision ID: 597ee3b96465
Revises: 396ab17b8d19
Create Date: 2012-09-28 11:55:41.022309

"""

# revision identifiers, used by Alembic.
revision = '597ee3b96465'
down_revision = '396ab17b8d19'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('TicketPrintHistory', sa.Column('order_id', Identifier(), nullable=True))
    op.create_foreign_key('TicketPrintHistory_ibfk_6', 'TicketPrintHistory', 'Order', ['order_id'], ['id'], onupdate='CASCADE', ondelete='CASCADE')

def downgrade():
    op.drop_constraint('TicketPrintHistory_ibfk_6', 'TicketPrintHistory', type='foreignkey')
    op.drop_column('TicketPrintHistory', 'order_id')
