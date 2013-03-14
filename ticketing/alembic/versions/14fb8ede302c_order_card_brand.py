"""Order.card_brand

Revision ID: 14fb8ede302c
Revises: 3e251dc4cbb7
Create Date: 2013-03-07 16:41:42.556471

"""

# revision identifiers, used by Alembic.
revision = '14fb8ede302c'
down_revision = '3e251dc4cbb7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("Order",
        sa.Column('card_brand', sa.Unicode(20)),
    )

def downgrade():
    op.drop_column("Order", "card_brand")
