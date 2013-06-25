"""create index SejOrder.order_id multicheckout_order_status.OrderNo

Revision ID: b6c72d434f9
Revises: 23d59b1d8131
Create Date: 2013-06-25 22:33:32.067146

"""

# revision identifiers, used by Alembic.
revision = 'b6c72d434f9'
down_revision = '23d59b1d8131'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('ix_SejOrder_order_id', 'SejOrder', ['order_id'])
    op.create_index('ix_multicheckout_order_status_OrderNo', 'multicheckout_order_status', ['OrderNo'])

def downgrade():
    op.drop_index('ix_multicheckout_order_status_OrderNo', 'multicheckout_order_status')
    op.drop_index('ix_SejOrder_order_id', 'SejOrder')
