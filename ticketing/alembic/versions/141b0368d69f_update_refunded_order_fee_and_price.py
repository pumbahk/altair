"""update refunded order fee and price

Revision ID: 141b0368d69f
Revises: 412fc1966fca
Create Date: 2014-06-03 12:31:38.521786

"""

# revision identifiers, used by Alembic.
revision = '141b0368d69f'
down_revision = '412fc1966fca'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''
               UPDATE `Order` o,
                      `OrderedProduct` op,
                      `OrderedProductItem` opi,
                      `Order` old_o,
                      `OrderedProduct` old_op,
                      `OrderedProductItem` old_opi
               SET o.total_amount    = old_o.total_amount,
                   o.system_fee      = old_o.system_fee,
                   o.transaction_fee = old_o.transaction_fee,
                   o.delivery_fee    = old_o.delivery_fee,
                   o.special_fee     = old_o.special_fee,
                   op.price          = old_op.price,
                   opi.price         = old_opi.price
               WHERE o.id = op.order_id
                 AND op.id = opi.ordered_product_id
                 AND old_o.id = old_op.order_id
                 AND old_op.id = old_opi.ordered_product_id
                 AND o.order_no = old_o.order_no
                 AND op.product_id = old_op.product_id
                 AND opi.product_item_id = old_opi.product_item_id
                 AND o.branch_no > 1
                 AND o.refund_id IS NOT NULL
                 AND o.refunded_at IS NOT NULL
                 AND o.deleted_at IS NULL
                 AND (o.branch_no - 1) = old_o.branch_no
                 AND old_o.refund_id IS NOT NULL
                 AND old_o.refunded_at IS NULL
                 AND old_o.deleted_at IS NOT NULL
               ''')

def downgrade():
    op.execute('''
               UPDATE `Order` o,
                      `OrderedProduct` op,
                      `OrderedProductItem` opi,
                      `Order` old_o,
                      `OrderedProduct` old_op,
                      `OrderedProductItem` old_opi
               SET o.total_amount    = o.original_total_amount,
                   o.system_fee      = o.original_system_fee,
                   o.transaction_fee = o.original_transaction_fee,
                   o.delivery_fee    = o.original_delivery_fee,
                   o.special_fee     = o.original_special_fee,
                   op.price          = op.original_price,
                   opi.price         = opi.original_price,
               WHERE o.id = op.order_id
                 AND op.id = opi.ordered_product_id
                 AND old_o.id = old_op.order_id
                 AND old_op.id = old_opi.ordered_product_id
                 AND o.order_no = old_o.order_no
                 AND op.product_id = old_op.product_id
                 AND opi.product_item_id = old_opi.product_item_id
                 AND o.branch_no > 1
                 AND o.refund_id IS NOT NULL
                 AND o.refunded_at IS NOT NULL
                 AND o.deleted_at IS NULL
                 AND (o.branch_no - 1) = old_o.branch_no
                 AND old_o.refund_id IS NOT NULL
                 AND old_o.refunded_at IS NULL
                 AND old_o.deleted_at IS NOT NULL
               ''')
