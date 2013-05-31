"""LotEntry.canceled_at

Revision ID: 2a0994d0826
Revises: 35f24964b70c
Create Date: 2013-05-14 17:01:17.249667

"""

# revision identifiers, used by Alembic.
revision = '2a0994d0826'
down_revision = '35f24964b70c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotEntry",
                  sa.Column("canceled_at", sa.DateTime))
    op.add_column("LotEntryWish",
                  sa.Column("canceled_at", sa.DateTime))

def downgrade():
    op.drop_column("LotEntry", "canceled_at")
    op.drop_column("LotEntryWish", "canceled_at")

