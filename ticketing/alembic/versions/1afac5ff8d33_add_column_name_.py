"""add column name ExternalSerialCodeSetting

Revision ID: 1afac5ff8d33
Revises: 4935d7c2fdf6
Create Date: 2020-09-17 17:19:03.058988

"""

# revision identifiers, used by Alembic.
revision = '1afac5ff8d33'
down_revision = '4935d7c2fdf6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ExternalSerialCodeSetting', sa.Column('name', sa.String(length=255), nullable=True, default=''))


def downgrade():
    op.drop_column('ExternalSerialCodeSetting', 'name')
