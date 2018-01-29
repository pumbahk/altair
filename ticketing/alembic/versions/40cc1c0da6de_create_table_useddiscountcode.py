"""create table UsedDiscountCode

Revision ID: 40cc1c0da6de
Revises: 4cef5d7f0122
Create Date: 2017-12-07 20:31:58.109472

"""

# revision identifiers, used by Alembic.
revision = '40cc1c0da6de'
down_revision = '4cef5d7f0122'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
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


def downgrade():
    op.drop_table('UsedDiscountCode')

