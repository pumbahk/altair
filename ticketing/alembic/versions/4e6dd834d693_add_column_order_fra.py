"""add column Order.fraud_suspect

Revision ID: 4e6dd834d693
Revises: 30449e9b3ea9
Create Date: 2013-10-07 10:52:17.080494

"""

# revision identifiers, used by Alembic.
revision = '4e6dd834d693'
down_revision = '30449e9b3ea9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Order', sa.Column('fraud_suspect', sa.Boolean(), nullable=True, default=None))

def downgrade():
    op.drop_column('Order', 'fraud_suspect')
