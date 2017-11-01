"""add display order to SalesSegmentGroup

Revision ID: 3e7e61dda3ef
Revises: 7d530c296b4
Create Date: 2017-10-31 10:28:01.898823

"""

# revision identifiers, used by Alembic.
revision = '3e7e61dda3ef'
down_revision = '7d530c296b4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroup', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default=text('1')))

def downgrade():
    op.drop_column('SalesSegmentGroup', 'display_order')