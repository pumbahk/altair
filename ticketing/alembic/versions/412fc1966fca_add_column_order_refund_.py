"""add_column Order.refund_

Revision ID: 412fc1966fca
Revises: 379d8f5fb25
Create Date: 2014-06-03 11:30:21.477743

"""

# revision identifiers, used by Alembic.
revision = '412fc1966fca'
down_revision = '379d8f5fb25'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Order', sa.Column(u'refund_total_amount', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'refund_system_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'refund_transaction_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'refund_delivery_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'refund_special_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'OrderedProduct', sa.Column(u'refund_price', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'OrderedProductItem', sa.Column(u'refund_price', sa.Numeric(precision=16, scale=2), nullable=False))

    op.add_column(u'Order', sa.Column(u'original_total_amount', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'original_system_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'original_transaction_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'original_delivery_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'Order', sa.Column(u'original_special_fee', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'OrderedProduct', sa.Column(u'original_price', sa.Numeric(precision=16, scale=2), nullable=False))
    op.add_column(u'OrderedProductItem', sa.Column(u'original_price', sa.Numeric(precision=16, scale=2), nullable=False))

    op.execute('''
               UPDATE `Order` o,
                      `OrderedProduct` op,
                      `OrderedProductItem` opi,
                      `Order` old_o,
                      `OrderedProduct` old_op,
                      `OrderedProductItem` old_opi
               SET o.refund_total_amount    = old_o.total_amount    - o.total_amount,
                   o.refund_system_fee      = old_o.system_fee      - o.system_fee,
                   o.refund_transaction_fee = old_o.transaction_fee - o.transaction_fee,
                   o.refund_delivery_fee    = old_o.delivery_fee    - o.delivery_fee,
                   o.refund_special_fee     = old_o.special_fee     - o.special_fee,
                   op.refund_price          = old_op.price          - op.price,
                   opi.refund_price         = old_opi.price         - opi.price,
                   o.original_total_amount    = o.total_amount,
                   o.original_system_fee      = o.system_fee,
                   o.original_transaction_fee = o.transaction_fee,
                   o.original_delivery_fee    = o.delivery_fee,
                   o.original_special_fee     = o.special_fee,
                   op.original_price          = op.price,
                   opi.original_price         = opi.price
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
    op.drop_column(u'Order', u'refund_total_amount')
    op.drop_column(u'Order', u'refund_system_fee')
    op.drop_column(u'Order', u'refund_transaction_fee')
    op.drop_column(u'Order', u'refund_delivery_fee')
    op.drop_column(u'Order', u'refund_special_fee')
    op.drop_column(u'OrderedProduct', u'refund_price')
    op.drop_column(u'OrderedProductItem', u'refund_price')

    op.drop_column(u'Order', u'original_total_amount')
    op.drop_column(u'Order', u'original_system_fee')
    op.drop_column(u'Order', u'original_transaction_fee')
    op.drop_column(u'Order', u'original_delivery_fee')
    op.drop_column(u'Order', u'original_special_fee')
    op.drop_column(u'OrderedProduct', u'original_price')
    op.drop_column(u'OrderedProductItem', u'original_price')
