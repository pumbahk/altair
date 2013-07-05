"""Lot.auth_type

Revision ID: 4838962beb11
Revises: e2b33ce85de
Create Date: 2013-06-20 14:20:31.209671

"""

# revision identifiers, used by Alembic.
revision = '4838962beb11'
down_revision = '134458f9ae23'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("Lot",
                  sa.Column("auth_type", sa.Unicode(255)))


def downgrade():
    op.drop_column("Lot", "auth_type")
