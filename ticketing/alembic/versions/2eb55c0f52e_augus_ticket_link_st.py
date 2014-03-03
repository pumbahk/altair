"""augus_ticket_link_st

Revision ID: 2eb55c0f52e
Revises: 521506639053
Create Date: 2014-02-19 11:55:24.602964

"""

# revision identifiers, used by Alembic.
revision = '2eb55c0f52e'
down_revision = '521506639053'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('AugusStockInfo',
                  sa.Column('augus_ticket_id', Identifier(), nullable=False))

def downgrade():
    op.drop_column('AugusStockInfo', 'augus_ticket_id')
