"""lots

Revision ID: 1782323b168c
Revises: 54d62937d132
Create Date: 2012-11-29 16:02:19.264834

"""

# revision identifiers, used by Alembic.
revision = '1782323b168c'
down_revision = '481d8345edac'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Lot',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=True),
    sa.Column('limit_wishes', sa.Integer(), nullable=True),
    sa.Column('event_id', Identifier(), nullable=True),
    sa.Column('selection_type', sa.Integer(), nullable=True),
    sa.Column('sales_segment_id', Identifier(), nullable=True),
    sa.Column('status', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['Event.id'], name="Lot_ibfk_1"),
    sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], name="Lot_ibfk_2"),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('Lots_StockType',
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('stock_type_id', Identifier(), nullable=True),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="Lots_StockType__ibfk_1"),
    sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], name="Lots_StockType__ibfk_2"),
    sa.PrimaryKeyConstraint()
    )
    op.create_table('Lots_Performance',
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('performance_id', Identifier(), nullable=True),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="Lots_Performance_ibfk_1"),
    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="Lots_Performance_ibfk_2"),
    sa.PrimaryKeyConstraint()
    )
    op.create_table('LotEntry',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('entry_no', sa.Unicode(length=20), nullable=True),
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('shipping_address_id', Identifier(), nullable=True),
    sa.Column('membergroup_id', Identifier(), nullable=True),
    sa.Column('elected_at', sa.DateTime(), nullable=True),
    sa.Column('rejected_at', sa.DateTime(), nullable=True),
    sa.Column('cart_id', Identifier(), nullable=True),
    sa.Column('order_id', Identifier(), nullable=True),
    sa.Column('payment_delivery_method_pair_id', Identifier(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['cart_id'], ['ticketing_carts.id'], name="LotEntry_ibfk_1"),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="LotEntry_ibfk_2"),
    sa.ForeignKeyConstraint(['membergroup_id'], ['MemberGroup.id'], name="LotEntry_ibfk_3"),
    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], name="LotEntry_ibfk_4"),
    sa.ForeignKeyConstraint(['shipping_address_id'], ['ShippingAddress.id'], name="LotEntry_ibfk_5"),
    sa.ForeignKeyConstraint(['payment_delivery_method_pair_id'], ['PaymentDeliveryMethodPair.id'], name="LotEntry_ibfk_6"),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('entry_no')
    )
    op.create_table('LotEntryWish',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('wish_order', sa.Integer(), nullable=True),
    sa.Column('entry_wish_no', sa.Unicode(length=30), nullable=True),
    sa.Column('performance_id', Identifier(), nullable=True),
    sa.Column('lot_entry_id', Identifier(), nullable=True),
    sa.Column('elected_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['lot_entry_id'], ['LotEntry.id'], name="LotEntryWish_ibfk_1"),
    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="LotEntryWish_ibfk_2"),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('LotEntryProduct',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=True),
    sa.Column('product_id', Identifier(), nullable=True),
    sa.Column('lot_wish_id', Identifier(), nullable=True),
    sa.Column('performance_id', Identifier(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['lot_wish_id'], ['LotEntryWish.id'], name="LotEntryProduct_ibfk_1"),
    sa.ForeignKeyConstraint(['product_id'], ['Product.id'], name="LotEntryProduct_ibfk_2"),
    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="LotEntryProduct_ibfk_3"),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('LotElectedEntry',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('lot_entry_id', Identifier(), nullable=True),
    sa.Column('lot_entry_wish_id', Identifier(), nullable=True),
    sa.Column('mail_sent_at', sa.DateTime(), nullable=True),
    sa.Column('order_id', Identifier(), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['lot_entry_id'], ['LotEntry.id'], name="LotElectedEntry_ibfk_1"),
    sa.ForeignKeyConstraint(['lot_entry_wish_id'], ['LotEntryWish.id'], name="LotElectedEntry_ibfk_2"),
    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], name="LotElectedEntry_ibfk_3"),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('LotElectWork',
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('lot_entry_no', sa.Unicode(length=20), nullable=True),
    sa.Column('wish_order', sa.Integer(), nullable=True),
    sa.Column('entry_wish_no', sa.Unicode(length=30), nullable=True),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['lot_entry_no'], ['LotEntry.entry_no'], name="LotElectWork_ibfk_1"),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="LotElectWork_ibfk_2"),
    #sa.ForeignKeyConstraint(['wish_order'], ['LotEntryWish.wish_order'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lot_entry_no')
    )
    ### end Alembic commands ###

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('LotElectWork')
    op.drop_table('LotElectedEntry')
    op.drop_table('LotEntryProduct')
    op.drop_table('LotEntryWish')
    op.drop_table('LotEntry')
    op.drop_table('Lots_Performance')
    op.drop_table('Lots_StockType')
    op.drop_table('Lot')
    ### end Alembic commands ###
