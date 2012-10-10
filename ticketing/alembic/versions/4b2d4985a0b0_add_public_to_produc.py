"""add public to product

Revision ID: 4b2d4985a0b0
Revises: 2aa4d646b5fd
Create Date: 2012-10-10 23:42:43.380723

"""

# revision identifiers, used by Alembic.
revision = '4b2d4985a0b0'
down_revision = '2aa4d646b5fd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('Product', sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')))

def downgrade():
    op.drop_column('Product', 'public')
