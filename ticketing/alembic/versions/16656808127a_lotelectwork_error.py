"""LotElectWork.error

Revision ID: 16656808127a
Revises: 80797931bae
Create Date: 2013-05-20 18:19:06.664663

"""

# revision identifiers, used by Alembic.
revision = '16656808127a'
down_revision = '80797931bae'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotElectWork",
                  sa.Column("error", sa.UnicodeText))


def downgrade():
    op.drop_column("LotElectWork", "error")
