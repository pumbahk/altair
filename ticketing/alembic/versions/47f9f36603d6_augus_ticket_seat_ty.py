"""augus_ticket_seat_type

Revision ID: 47f9f36603d6
Revises: 493be3f09c7a
Create Date: 2014-01-21 11:41:07.621841

"""

# revision identifiers, used by Alembic.
revision = '47f9f36603d6'
down_revision = '493be3f09c7a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('AugusTicket', sa.Column('stock_type_id', Identifier, default=None, nullable=True))

def downgrade():
    op.drop_column('AugusTicket', 'stock_type_id')
