"""#TKT101 add withdrawn_at to LotEntry, LotEntryWish

Revision ID: 6cdbdb8cd27
Revises: 4f0f7a1dc72e
Create Date: 2015-10-19 20:20:25.108530

"""

# revision identifiers, used by Alembic.
revision = '6cdbdb8cd27'
down_revision = '4f0f7a1dc72e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotEntry",
                  sa.Column("withdrawn_at", sa.DateTime))
    op.add_column("LotEntryWish",
                  sa.Column("withdrawn_at", sa.DateTime))

def downgrade():
    op.drop_column("LotEntry", "withdrawn_at")
    op.drop_column("LotEntryWish", "withdrawn_at")
