"""add i18n column to OrganizationSetting

Revision ID: 4a99f47c1bd4
Revises: 4fdd3d5caa94
Create Date: 2016-05-25 14:34:30.786634

"""

# revision identifiers, used by Alembic.
revision = '4a99f47c1bd4'
down_revision = '4fdd3d5caa94'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('i18n', sa.Boolean(), nullable=False, default=False, server_default=text('0')))

def downgrade():
    op.drop_column('OrganizationSetting', 'i18n')
