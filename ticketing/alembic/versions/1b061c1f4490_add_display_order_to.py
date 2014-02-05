"""add_display_order_to_event

Revision ID: 1b061c1f4490
Revises: 23dc7707136d
Create Date: 2014-02-04 10:12:56.721418

"""

# revision identifiers, used by Alembic.
revision = '1b061c1f4490'
down_revision = '23dc7707136d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Event', sa.Column('display_order', sa.Integer(), nullable=False, default=1))

def downgrade():
    op.drop_column('Event', 'display_order')
