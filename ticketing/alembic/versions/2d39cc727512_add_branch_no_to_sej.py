"""add_branch_no_to_sej_order

Revision ID: 2d39cc727512
Revises: 574153c1e09b
Create Date: 2013-09-30 15:59:23.065299

"""

# revision identifiers, used by Alembic.
revision = '2d39cc727512'
down_revision = '574153c1e09b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SejTicket', sa.Column('order_no', sa.String(12), nullable=False))
    op.execute('UPDATE SejTicket, SejOrder SET SejTicket.order_no=SejOrder.order_no WHERE SejTicket.order_id=SejOrder.id')
    op.drop_constraint('SejTicket_ibfk_1', 'SejTicket', type_='foreignkey')
    op.drop_index('order_id', 'SejTicket')
    op.drop_column('SejTicket', 'order_id')
    op.create_foreign_key('SejTicket_ibfk_1', 'SejTicket', 'SejOrder', ['order_no'], ['order_no'])
    op.add_column('SejOrder', sa.Column('branch_no', sa.Integer(), nullable=False, default=1, server_default='1'))
    op.execute("DELETE FROM `SejTicket` WHERE order_no='';"),
    op.execute("DELETE FROM `SejOrder` WHERE order_no='';"),
    op.create_unique_constraint('ix_SejOrder_order_no_branch_no', 'SejOrder', ['order_no', 'branch_no'])

def downgrade():
    op.add_column('SejTicket', sa.Column('order_id', Identifier, nullable=False))
    op.execute('UPDATE SejTicket, SejOrder SET SejTicket.order_id=SejOrder.id WHERE SejTicket.order_no=SejOrder.order_no')
    op.drop_constraint('SejTicket_ibfk_1', 'SejTicket', type_='foreignkey')
    op.drop_index('SejTicket_ibfk_1', 'SejTicket')
    op.drop_column('SejTicket', 'order_no')
    op.create_index('order_id', 'SejTicket', ['order_id'])
    op.create_foreign_key('SejTicket_ibfk_1', 'SejTicket', 'SejOrder', ['order_id'], ['id'])
    op.drop_constraint('ix_SejOrder_order_no_branch_no', 'SejOrder', type_='unique')
    op.drop_column('SejOrder', 'branch_no')
