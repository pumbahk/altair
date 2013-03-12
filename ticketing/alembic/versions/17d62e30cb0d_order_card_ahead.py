"""Order.card_ahead

Revision ID: 17d62e30cb0d
Revises: 14fb8ede302c
Create Date: 2013-03-07 18:19:18.386681

"""

# revision identifiers, used by Alembic.
revision = '17d62e30cb0d'
down_revision = '14fb8ede302c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("Order",
        sa.Column("card_ahead_com_code", sa.Unicode(20)))
    op.add_column("Order",
        sa.Column("card_ahead_com_name", sa.Unicode(20)))


def downgrade():
    op.drop_column("Order", "card_ahead_com_code")
    op.drop_column("Order", "card_ahead_com_name")
