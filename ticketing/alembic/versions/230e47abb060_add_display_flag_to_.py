"""add display flag to stock type

Revision ID: 230e47abb060
Revises: 53af2f49cb08
Create Date: 2013-09-02 10:56:51.494363

"""

# revision identifiers, used by Alembic.
revision = '230e47abb060'
down_revision = '53af2f49cb08'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('StockType', sa.Column('display', sa.Boolean(True)))


def downgrade():
    op.drop_column('StockType', 'display')
