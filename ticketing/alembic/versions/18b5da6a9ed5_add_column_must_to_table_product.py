"""add column must to table product

Revision ID: 18b5da6a9ed5
Revises: 3be1e0e661cc
Create Date: 2015-03-26 17:42:32.239419

"""

# revision identifiers, used by Alembic.
revision = '18b5da6a9ed5'
down_revision = '3be1e0e661cc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Product', sa.Column('must_be_chosen', sa.Boolean(), nullable=False, default=False, server_default='0'))
def downgrade():
    op.drop_column('Product', 'must_be_chosen')
