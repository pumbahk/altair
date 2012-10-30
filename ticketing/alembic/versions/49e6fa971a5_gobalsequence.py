"""GobalSequence

Revision ID: 49e6fa971a5
Revises: 2f4b1cc03cc5
Create Date: 2012-10-29 23:54:57.118078

"""

# revision identifiers, used by Alembic.
revision = '49e6fa971a5'
down_revision = '2f4b1cc03cc5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.sql import table

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        "GlobalSequence",
        sa.Column("id", Identifier, primary_key=True),
        sa.Column("name", sa.Unicode(255)),
        sa.Column("value", sa.BigInteger()),
        # WithTimestamp
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        # LogicallyDeleted
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.UniqueConstraint('name', name="uk_GlobalSequence_name"))

    op.bulk_insert(
        table("GlobalSequence",
            sa.Column("name", sa.Unicode(255)),
            sa.Column("value", sa.BigInteger())),
        [
            {'name': u'order_no', 'value': 10000,}
        ])

def downgrade():
    op.drop_table("GlobalSequence")
