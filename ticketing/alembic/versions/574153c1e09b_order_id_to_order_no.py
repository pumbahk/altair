"""order_id_to_order_no

Revision ID: 574153c1e09b
Revises: 4ca796782d0a
Create Date: 2013-09-30 14:50:58.349274

"""

# revision identifiers, used by Alembic.
revision = '574153c1e09b'
down_revision = '4ca796782d0a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_index('ix_SejOrder_order_id', 'SejOrder')
    op.alter_column(
        'SejOrder',
        'order_id',
        new_column_name='order_no',
        existing_type=sa.String(12),
        existing_nullable=False)
    op.create_index('ix_SejOrder_order_no', 'SejOrder', ['order_no'])
    op.alter_column(
        'SejNotification',
        'order_id',
        new_column_name='order_no',
        existing_type=sa.String(12),
        existing_nullable=False)
    op.alter_column(
        'SejRefundTicket',
        'order_id',
        new_column_name='order_no',
        existing_type=sa.String(12),
        existing_nullable=False)

def downgrade():
    op.drop_index('ix_SejOrder_order_no', 'SejOrder')
    op.alter_column(
        'SejOrder',
        'order_no',
        new_column_name='order_id',
        existing_type=sa.String(12),
        existing_nullable=False)
    op.create_index('ix_SejOrder_order_id', 'SejOrder', ['order_id'])
    op.alter_column(
        'SejNotification',
        'order_no',
        new_column_name='order_id',
        existing_type=sa.String(12),
        existing_nullable=False)
    op.alter_column(
        'SejRefundTicket',
        'order_no',
        new_column_name='order_id',
        existing_type=sa.String(12),
        existing_nullable=False)
