"""SalesSegment[Group].auth3d_notice

Revision ID: 399b88245d9
Revises: 304ea58e981
Create Date: 2013-07-31 18:05:59.908638

"""

# revision identifiers, used by Alembic.
revision = '399b88245d9'
down_revision = '304ea58e981'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("SalesSegment",
                  sa.Column("auth3d_notice", sa.UnicodeText),
                  )
    op.add_column("SalesSegmentGroup",
                  sa.Column("auth3d_notice", sa.UnicodeText),
                  )

def downgrade():
    op.drop_column("SalesSegmentGroup", "auth3d_notice")
    op.drop_column("SalesSegment", "auth3d_notice")

