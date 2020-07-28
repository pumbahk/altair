"""alter talbe Operator add hide

Revision ID: 400b8d1e91cd
Revises: 11911dbcc8ea
Create Date: 2020-07-27 12:16:47.107102

"""

# revision identifiers, used by Alembic.
revision = '400b8d1e91cd'
down_revision = '11911dbcc8ea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Operator',
                  sa.Column('hide', sa.Boolean(), nullable=True, default=False, server_default=text('0')))


def downgrade():
    op.drop_column('Operator', 'hide')
