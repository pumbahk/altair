"""create index on FamiPortReceipt created_at

Revision ID: eaa84e4df3d
Revises: 2b133f03a24c
Create Date: 2019-02-15 14:34:20.519989

"""

# revision identifiers, used by Alembic.
revision = 'eaa84e4df3d'
down_revision = '2b133f03a24c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('created_at', 'FamiPortReceipt', ['created_at'])


def downgrade():
    op.drop_index('created_at', 'FamiPortReceipt')
