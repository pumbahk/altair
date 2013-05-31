"""drop  Seat_SeatAdjacency

Revision ID: 52e2400a2c14
Revises: 1830c3b36cba
Create Date: 2013-05-15 13:29:12.503355

"""

# revision identifiers, used by Alembic.
revision = '52e2400a2c14'
down_revision = '1830c3b36cba'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_table('Seat_SeatAdjacency')
    op.drop_constraint('SeatAdjacencySet_ibfk_1', 'SeatAdjacencySet', type='foreignkey')
    op.drop_column(u'SeatAdjacencySet', 'venue_id')

def downgrade():
    pass
