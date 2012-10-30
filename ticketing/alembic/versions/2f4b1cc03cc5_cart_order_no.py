"""cart.order_no

Revision ID: 2f4b1cc03cc5
Revises: 39afb211aeec
Create Date: 2012-10-29 23:01:50.530602

"""

# revision identifiers, used by Alembic.
revision = '2f4b1cc03cc5'
down_revision = '39afb211aeec'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ticketing_carts', sa.Column('order_no', sa.String(255)))

def downgrade():
    op.drop_column('ticketing_carts', 'order_no')
