"""PageFormat add column display_order

Revision ID: 3be1e0e661cc
Revises: 489f1d6722a5
Create Date: 2015-03-19 15:40:29.847840

"""

# revision identifiers, used by Alembic.
revision = '3be1e0e661cc'
down_revision = '489f1d6722a5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('PageFormat', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default=text('1')))


def downgrade():
    op.drop_column('PageFormat', 'display_order')
