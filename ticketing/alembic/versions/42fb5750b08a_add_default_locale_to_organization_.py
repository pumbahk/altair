"""add default locale to organization setting

Revision ID: 42fb5750b08a
Revises: 572b22d533d6
Create Date: 2018-04-17 11:17:37.530456

"""

# revision identifiers, used by Alembic.
revision = '42fb5750b08a'
down_revision = '572b22d533d6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'OrganizationSetting', sa.Column('default_locale', sa.Unicode(length=255), nullable=False, server_default=u'ja'))

def downgrade():
    op.drop_column(u'OrganizationSetting', 'default_locale')
