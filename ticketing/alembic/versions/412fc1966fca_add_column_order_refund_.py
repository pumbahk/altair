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
    op.execute('''
               ALTER TABLE `Order` ADD COLUMN refund_total_amount NUMERIC(16, 2) NOT NULL,
                                   ADD COLUMN refund_system_fee NUMERIC(16, 2) NOT NULL,
                                   ADD COLUMN refund_transaction_fee NUMERIC(16, 2) NOT NULL,
                                   ADD COLUMN refund_delivery_fee NUMERIC(16, 2) NOT NULL,
                                   ADD COLUMN refund_special_fee NUMERIC(16, 2) NOT NULL,
                                   ADD COLUMN released_at datetime DEFAULT NULL
               ''')
    op.execute('''
               ALTER TABLE `OrderedProduct` ADD COLUMN refund_price NUMERIC(16, 2) NOT NULL
               ''')
    op.execute('''
               ALTER TABLE `OrderedProductItem` ADD COLUMN refund_price NUMERIC(16, 2) NOT NULL
               ''')
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
                   opi.refund_price         = old_opi.price         - opi.price
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

    op.create_table(
        u'tmp_order_fee_and_price',
        sa.Column(u'order_id', Identifier, primary_key=True),
        sa.Column(u'ordered_product_id', Identifier, primary_key=True),
        sa.Column(u'ordered_product_item_id', Identifier, primary_key=True),
        sa.Column(u'total_amount', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'system_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'transaction_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'delivery_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'special_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'ordered_product_price', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column(u'ordered_product_item_price', sa.Numeric(precision=16, scale=2), nullable=True)
        )
    op.execute('''
               INSERT INTO tmp_order_fee_and_price (
                   order_id,
                   ordered_product_id,
                   ordered_product_item_id,
                   total_amount,
                   system_fee,
                   transaction_fee,
                   delivery_fee,
                   special_fee,
                   ordered_product_price,
                   ordered_product_item_price
               ) SELECT
                   o.id,
                   op.id,
                   opi.id,
                   o.total_amount,
                   o.system_fee,
                   o.transaction_fee,
                   o.delivery_fee,
                   o.special_fee,
                   op.price,
                   opi.price
               FROM `Order` o,
                    `OrderedProduct` op,
                    `OrderedProductItem` opi
               WHERE o.id = op.order_id
                 AND op.id = opi.ordered_product_id
                 AND o.branch_no > 1
                 AND o.refund_id IS NOT NULL
                 AND o.refunded_at IS NOT NULL
                 AND o.deleted_at IS NULL
               ''')

def downgrade():
    op.drop_column(u'Order', u'refund_total_amount')
    op.drop_column(u'Order', u'refund_system_fee')
    op.drop_column(u'Order', u'refund_transaction_fee')
    op.drop_column(u'Order', u'refund_delivery_fee')
    op.drop_column(u'Order', u'refund_special_fee')
    op.drop_column(u'Order', u'released_at')
    op.drop_column(u'OrderedProduct', u'refund_price')
    op.drop_column(u'OrderedProductItem', u'refund_price')
    op.drop_table(u'tmp_order_fee_and_price')
