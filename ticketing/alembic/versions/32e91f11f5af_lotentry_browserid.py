"""LotEntry.browserid

Revision ID: 32e91f11f5af
Revises: edfd0a4da51
Create Date: 2013-05-28 15:35:03.734391

"""

# revision identifiers, used by Alembic.
revision = '32e91f11f5af'
down_revision = 'edfd0a4da51'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotEntry",
                  sa.Column("browserid", sa.String(40)))


def downgrade():
    op.drop_column("LotEntry", "browserid")
