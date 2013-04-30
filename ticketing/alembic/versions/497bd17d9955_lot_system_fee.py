"""Lot.system_fee

Revision ID: 497bd17d9955
Revises: 553d9a30af4a
Create Date: 2013-04-26 18:11:34.789841

"""

# revision identifiers, used by Alembic.
revision = '497bd17d9955'
down_revision = '553d9a30af4a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Lot',
                  sa.Column("system_fee", sa.Numeric(precision=16, scale=2),
                            default=text("0")))

def downgrade():
    op.drop_column('Lot', 'system_fee')
