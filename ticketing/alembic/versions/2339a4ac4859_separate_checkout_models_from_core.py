"""separate_checkout_models_from_core

Revision ID: 2339a4ac4859
Revises: 141b0368d69f
Create Date: 2014-06-03 16:50:09.820796

"""

# revision identifiers, used by Alembic.
revision = '2339a4ac4859'
down_revision = '141b0368d69f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Checkout', sa.Column('_orderCartId', sa.Unicode(255), nullable=False))
    op.add_column('Checkout', sa.Column('authorized_at', sa.DateTime(), nullable=True))
    op.execute('UPDATE Checkout JOIN Cart ON Checkout.orderCartId=Cart.id SET _orderCartId=Cart.order_no')
    op.create_index('idx_orderCartId', 'Checkout', ['_orderCartId'])
    op.drop_constraint('Checkout_ibfk_1', 'Checkout', type_='foreignkey')

def downgrade():
    op.drop_index('idx_orderCartId', 'Checkout')
    op.drop_column('Checkout', '_orderCartId')
    op.drop_column('Checkout', 'authorized_at')
    op.create_foreign_key('Checkout_ibfk_1', 'Checkout', 'Cart', ['orderCartId'], ['id'], ondelete='CASCADE')
