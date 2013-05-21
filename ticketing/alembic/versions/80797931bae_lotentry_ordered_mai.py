"""LotEntry.ordered_mail_sent_at

Revision ID: 80797931bae
Revises: 52e2400a2c14
Create Date: 2013-05-20 16:38:39.499531

"""

# revision identifiers, used by Alembic.
revision = '80797931bae'
down_revision = '52e2400a2c14'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("LotEntry",
                  sa.Column("ordered_mail_sent_at", sa.DateTime()))

def downgrade():
    op.drop_column("LotEntry", "ordered_mail_sent_at")
