"""add default locale to organization setting

Revision ID: 42fb5750b08a
Revises: 2f6a5a0b914b
Create Date: 2018-04-17 11:17:37.530456

"""

# revision identifiers, used by Alembic.
revision = '42fb5750b08a'
down_revision = '2f6a5a0b914b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'OrganizationSetting', sa.Column('default_locale', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column(u'OrganizationSetting', 'default_locale')
