"""add_sales_segment_to_order

Revision ID: 378db2b9f0bd
Revises: 26a290438f7e
Create Date: 2013-09-03 09:54:21.488788

"""

# revision identifiers, used by Alembic.
revision = '378db2b9f0bd'
down_revision = '26a290438f7e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(
        'Order',
        sa.Column(
            'sales_segment_id',
            Identifier(),
            sa.ForeignKey('SalesSegment.id', name='Order_ibfk_8'),
            nullable=True))
    op.execute('UPDATE `Order` JOIN `Cart` ON `Order`.id=`Cart`.order_id SET `Order`.sales_segment_id=`Cart`.sales_segment_id;');

def downgrade():
    op.drop_constraint('Order_ibfk_8', 'Order', type_='foreignkey')
    op.drop_column('Order', 'sales_segment_id')

