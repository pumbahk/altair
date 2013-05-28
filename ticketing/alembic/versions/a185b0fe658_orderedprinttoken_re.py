"""OrderedPrintToken.refreshed_at

Revision ID: a185b0fe658
Revises: edfd0a4da51
Create Date: 2013-05-28 16:00:04.903055

"""

# revision identifiers, used by Alembic.
revision = 'a185b0fe658'
down_revision = 'edfd0a4da51'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('OrderedProductItemToken', sa.Column('refreshed_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('OrderedProductItemToken', 'refreshed_at')
