"""LotEntryWish.rejected_at

Revision ID: 1830c3b36cba
Revises: 2a0994d0826
Create Date: 2013-05-15 17:38:21.765657

"""

# revision identifiers, used by Alembic.
revision = '1830c3b36cba'
down_revision = '2a0994d0826'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotEntryWish",
                  sa.Column("rejected_at", sa.DateTime()))

def downgrade():
    op.drop_column("LotEntryWish",
                   "rejected_at")
