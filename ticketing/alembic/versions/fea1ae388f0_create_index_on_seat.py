"""create index on SeatStatus updated_at

Revision ID: fea1ae388f0
Revises: e2b33ce85de
Create Date: 2013-06-18 19:56:26.015423

"""

# revision identifiers, used by Alembic.
revision = 'fea1ae388f0'
down_revision = 'e2b33ce85de'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('ix_SeatStatus_updated_at', 'SeatStatus', ['updated_at'])

def downgrade():
    op.drop_index('ix_SeatStatus_updated_at', 'SeatStatus')

