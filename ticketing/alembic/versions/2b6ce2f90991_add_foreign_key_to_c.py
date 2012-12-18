"""add foreign key to checkout

Revision ID: 2b6ce2f90991
Revises: 571c5b80b84c
Create Date: 2012-12-13 15:49:17.946816

"""

# revision identifiers, used by Alembic.
revision = '2b6ce2f90991'
down_revision = '571c5b80b84c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('Checkout', 'orderCartId', name='orderCartId', type_=Identifier(), existing_type=sa.Unicode())
    op.create_foreign_key('Checkout_ibfk_1', 'Checkout', 'ticketing_carts', ['orderCartId'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('Checkout_ibfk_1', 'Checkout', type='foreignkey')
    op.alter_column('Checkout', 'orderCartId', name='orderCartId', type_=sa.Unicode(20))

