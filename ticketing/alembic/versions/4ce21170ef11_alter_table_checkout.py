"""alter table Checkout add column

Revision ID: 4ce21170ef11
Revises: 51e772b5532c
Create Date: 2013-02-12 17:51:30.658518

"""

# revision identifiers, used by Alembic.
revision = '4ce21170ef11'
down_revision = '51e772b5532c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Checkout', sa.Column('sales_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column(u'Checkout', 'sales_at')
