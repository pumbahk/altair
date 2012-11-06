"""add_organization_short_name

Revision ID: 3aa73a04193d
Revises: 32092d560abc
Create Date: 2012-11-06 11:23:00.868584

"""

# revision identifiers, used by Alembic.
revision = '3aa73a04193d'
down_revision = '32092d560abc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column(u'Organization', sa.Column('short_name', sa.String(length=32), nullable=False, index=True))

def downgrade():
    op.drop_column(u'Organization', 'short_name')
