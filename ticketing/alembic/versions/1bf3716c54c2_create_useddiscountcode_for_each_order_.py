"""Create UsedDiscountCode for each order and cart

Revision ID: 1bf3716c54c2
Revises: 40cc1c0da6de
Create Date: 2017-12-15 19:25:19.333036

"""

# revision identifiers, used by Alembic.
revision = '1bf3716c54c2'
down_revision = '40cc1c0da6de'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_table('UsedDiscountCode')
    op.create_table(
        'UsedDiscountCodeCart',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_id', Identifier, nullable=True, index=True),
        sa.Column('code', sa.Unicode(12), nullable=True, index=True),
        sa.Column('carted_product_item_id', Identifier),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_id'], ['DiscountCode.id'], name="UsedDiscountCodeCart_ibfk_1"),
        sa.ForeignKeyConstraint(['carted_product_item_id'], ['CartedProductItem.id'], name="UsedDiscountCodeCart_ibfk_2"),
    )
    op.create_table(
        'UsedDiscountCodeOrder',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_id', Identifier, nullable=True, index=True),
        sa.Column('code', sa.Unicode(12), nullable=True, index=True),
        sa.Column('ordered_product_item_id', Identifier),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('canceled_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('refunded_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_id'], ['DiscountCode.id'], name="UsedDiscountCodeOrder_ibfk_1"),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], name="UsedDiscountCodeOrder_ibfk_2")
    )


def downgrade():
    op.drop_table('UsedDiscountCodeCart')
    op.drop_table('UsedDiscountCodeOrder')
    op.create_table(
        'UsedDiscountCode',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_id', Identifier, nullable=True, index=True),
        sa.Column('code', sa.Unicode(12), nullable=True, index=True),
        sa.Column('carted_product_item_id', Identifier),
        sa.Column('ordered_product_item_id', Identifier),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_id'], ['DiscountCode.id'], name="UsedDiscountCode_ibfk_1"),
        sa.ForeignKeyConstraint(['carted_product_item_id'], ['CartedProductItem.id'], name="UsedDiscountCode_ibfk_2"),
        sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'], name="UsedDiscountCode_ibfk_3")
    )