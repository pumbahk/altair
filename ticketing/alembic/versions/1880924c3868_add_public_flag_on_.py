"""Add public_flag on LivePerformanceSetting

Revision ID: 1880924c3868
Revises: 46d8b483857d
Create Date: 2020-09-07 17:54:19.436872

"""

# revision identifiers, used by Alembic.
revision = '1880924c3868'
down_revision = '46d8b483857d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LivePerformanceSetting',
                  sa.Column('public_flag', sa.Boolean, default=False, server_default=text('0')))

def downgrade():
    op.drop_column('LivePerformanceSetting', 'public_flag')
