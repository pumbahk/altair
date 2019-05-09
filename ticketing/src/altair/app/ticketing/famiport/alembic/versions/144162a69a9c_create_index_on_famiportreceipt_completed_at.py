"""create index on FamiPortReceipt completed_at

Revision ID: 144162a69a9c
Revises: eaa84e4df3d
Create Date: 2019-03-12 11:24:12.236337

"""

# revision identifiers, used by Alembic.
revision = '144162a69a9c'
down_revision = 'eaa84e4df3d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('completed_at', 'FamiPortReceipt', ['completed_at'])


def downgrade():
    op.drop_index('completed_at', 'FamiPortReceipt')
