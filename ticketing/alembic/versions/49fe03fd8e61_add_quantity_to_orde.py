"""add_quantity_to_ordered_product_item

Revision ID: 49fe03fd8e61
Revises: 4d71f19c4087
Create Date: 2012-09-20 13:45:37.035912

"""

# revision identifiers, used by Alembic.
revision = '49fe03fd8e61'
down_revision = '4d71f19c4087'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrderedProductItem', sa.Column('quantity', sa.Integer(), nullable=False, default=0, server_default='0'))
    op.execute('UPDATE OrderedProductItem, OrderedProduct, ProductItem SET OrderedProductItem.quantity=(OrderedProduct.quantity * ProductItem.quantity) WHERE OrderedProductItem.product_item_id=ProductItem.id AND OrderedProductItem.ordered_product_id=OrderedProduct.id;')

def downgrade():
    op.drop_column('OrderedProductItem', 'quantity')
