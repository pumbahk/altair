"""modify GlobalSequence

Revision ID: 32092d560abc
Revises: 43b4fece064c
Create Date: 2012-11-01 21:11:49.525650

"""

# revision identifiers, used by Alembic.
revision = '32092d560abc'
down_revision = '43b4fece064c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text, table
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_table(u'GlobalSequence')
    op.create_table(u'OrderNoSequence',
        sa.Column('id',
                Identifier,
               nullable=False),
        # WithTimestamp
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sqlf.current_timestamp()),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=text('0')),
        # LogicallyDeleted
        sa.Column('deleted_at', sa.TIMESTAMP, nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute('ALTER TABLE OrderNoSequence AUTO_INCREMENT = 10010')

def downgrade():
    op.drop_table(u'OrderNoSequence')
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
