"""add column PerformanceSetting.entry_limit

Revision ID: 53f29cc64fbf
Revises: 461b4010631c
Create Date: 2014-04-15 12:24:34.716840

"""

# revision identifiers, used by Alembic.
revision = '53f29cc64fbf'
down_revision = '461b4010631c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PerformanceSetting', sa.Column("entry_limit", sa.Integer(), nullable=True, default=text('NULL')))

def downgrade():
    op.drop_column('PerformanceSetting', 'entry_limit')
