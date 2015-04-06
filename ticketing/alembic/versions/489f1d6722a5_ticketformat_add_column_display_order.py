"""TicketFormat add column display_order

Revision ID: 489f1d6722a5
Revises: 492ca8fdfa1e
Create Date: 2015-03-13 12:02:33.219475

"""

# revision identifiers, used by Alembic.
revision = '489f1d6722a5'
down_revision = '492ca8fdfa1e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('TicketFormat', sa.Column('display_order', sa.Integer(), nullable=False, default=1))

def downgrade():
    op.drop_column('TicketFormat', 'display_order')
