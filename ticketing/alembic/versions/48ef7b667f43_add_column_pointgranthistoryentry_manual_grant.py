"""Add manual_grant column to PointGrantHistoryEntry

Revision ID: 48ef7b667f43
Revises: 2c844ed2c11
Create Date: 2014-09-12 11:03:50.577134

"""

# revision identifiers, used by Alembic.
revision = '48ef7b667f43'
down_revision = '2c844ed2c11'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'PointGrantHistoryEntry', sa.Column(u'manual_grant', sa.Boolean, nullable=False, default=False))

def downgrade():
    op.drop_column(u'PointGrantHistoryEntry', u'manual_grant')
