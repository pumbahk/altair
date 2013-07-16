"""order_limit

Revision ID: 33b55ed26f7c
Revises: 2d806a3a789
Create Date: 2013-07-16 18:05:48.876475

"""

# revision identifiers, used by Alembic.
revision = '33b55ed26f7c'
down_revision = '2d806a3a789'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegment",
                  sa.Column("order_limit", sa.Integer, default=text("0")))
    op.add_column("SalesSegmentGroup",
                  sa.Column("order_limit", sa.Integer, default=text("0")))

def downgrade():
    op.drop_column("SalesSegmentGroup", "order_limit")
    op.drop_column("SalesSegment", "order_limit")
