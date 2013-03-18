"""track browserid


Revision ID: 324a22883704
Revises: 56f5028103b1
Create Date: 2013-03-18 15:19:28.523181

"""

# revision identifiers, used by Alembic.
revision = '324a22883704'
down_revision = '56f5028103b1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Order',
        sa.Column('browserid', sa.String(40)))
    op.add_column('Cart',
        sa.Column('browserid', sa.String(40)))

def downgrade():
    op.drop_column('Order', 'browserid')
    op.drop_column('Cart', 'browserid')
