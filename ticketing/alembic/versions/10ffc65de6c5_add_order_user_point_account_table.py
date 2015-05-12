# encoding: utf-8
"""add_order_user_point_account_table

Revision ID: 10ffc65de6c5
Revises: 16c1183bb7e0
Create Date: 2015-04-24 17:57:14.090059

"""

# revision identifiers, used by Alembic.
revision = '10ffc65de6c5'
down_revision = '16c1183bb7e0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'Order_UserPointAccount',
        sa.Column('order_id', Identifier(), sa.ForeignKey('Order.id'), nullable=False),
        sa.Column('user_point_account_id', Identifier(), sa.ForeignKey('UserPointAccount.id'), nullable=False),
        sa.PrimaryKeyConstraint('order_id', 'user_point_account_id')
        )
    op.create_table(
        'ProtoOrder_UserPointAccount',
        sa.Column('proto_order_id', Identifier(), sa.ForeignKey('ProtoOrder.id'), nullable=False),
        sa.Column('user_point_account_id', Identifier(), sa.ForeignKey('UserPointAccount.id'), nullable=False),
        sa.PrimaryKeyConstraint('proto_order_id', 'user_point_account_id')
        )
    op.create_table(
        'Cart_UserPointAccount',
        sa.Column('cart_id', Identifier(), sa.ForeignKey('Cart.id'), nullable=False),
        sa.Column('user_point_account_id', Identifier(), sa.ForeignKey('UserPointAccount.id'), nullable=False),
        sa.PrimaryKeyConstraint('cart_id', 'user_point_account_id')
        )
    op.create_table(
        'LotEntry_UserPointAccount',
        sa.Column('lot_entry_id', Identifier(), sa.ForeignKey('LotEntry.id'), nullable=False),
        sa.Column('user_point_account_id', Identifier(), sa.ForeignKey('UserPointAccount.id'), nullable=False),
        sa.PrimaryKeyConstraint('lot_entry_id', 'user_point_account_id')
        )
    op.execute('INSERT INTO Order_UserPointAccount (order_id, user_point_account_id) SELECT `Order`.id order_id, `UserPointAccount`.id user_point_account_id FROM `Order` JOIN `UserPointAccount` ON `Order`.user_id=`UserPointAccount`.user_id WHERE `Order`.user_id IS NOT NULL')

def downgrade():
    op.drop_table('LotEntry_UserPointAccount')
    op.drop_table('Cart_UserPointAccount')
    op.drop_table('ProtoOrder_UserPointAccount')
    op.drop_table('Order_UserPointAccount')
