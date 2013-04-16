"""multicheckout_order_status.KeepAuthFor

Revision ID: 3ffc0a24682c
Revises: 3e1887488440
Create Date: 2013-04-15 10:51:34.815517

"""

# revision identifiers, used by Alembic.
revision = '3ffc0a24682c'
down_revision = '3e1887488440'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('multicheckout_order_status',
                  sa.Column('KeepAuthFor', sa.Unicode(20)))

def downgrade():
    op.drop_column('multicheckout_order_status',
                   'KeepAuthFor')
