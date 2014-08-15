"""drop_old_order_cart_id_from_checkout

Revision ID: 164ba9781aae
Revises: 470ecc52bc32
Create Date: 2014-07-07 10:13:16.162556

"""

# revision identifiers, used by Alembic.
revision = '164ba9781aae'
down_revision = '470ecc52bc32'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('Checkout', 'orderCartId')
    op.alter_column('Checkout', '_orderCartId',
        new_column_name='orderCartId',
        existing_type=sa.Unicode(255),
        existing_nullable=False
        )

def downgrade():
    op.alter_column('Checkout', 'orderCartId',
        new_column_name='_orderCartId',
        existing_type=sa.Unicode(255),
        existing_nullable=False
        )
    op.add_column('Checkout', sa.Column('orderCartId', Identifier(), nullable=True))
    op.execute('UPDATE Checkout JOIN Cart ON Checkout._orderCartId=Cart.order_no SET orderCartId=Cart.id')

