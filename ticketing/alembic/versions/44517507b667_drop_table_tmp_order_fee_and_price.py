"""drop table tmp_order_fee_and_price

Revision ID: 44517507b667
Revises: b73f93b4116
Create Date: 2014-06-13 13:16:01.287823

"""

# revision identifiers, used by Alembic.
revision = '44517507b667'
down_revision = 'b73f93b4116'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_table(u'tmp_order_fee_and_price')

def downgrade():
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
