"""LotErejectWork

Revision ID: edfd0a4da51
Revises: 16656808127a
Create Date: 2013-05-21 11:53:30.123946

"""

# revision identifiers, used by Alembic.
revision = 'edfd0a4da51'
down_revision = '16656808127a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table("LotRejectWork",
    sa.Column('id', Identifier(), nullable=False),
    sa.Column('lot_id', Identifier(), nullable=True),
    sa.Column('lot_entry_no', sa.Unicode(length=20), nullable=True),
    sa.Column("error", sa.UnicodeText),
    sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
    sa.ForeignKeyConstraint(['lot_entry_no'], ['LotEntry.entry_no'], name="LotRejectWork_ibfk_1"),
    sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="LotRejectWork_ibfk_2"),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('lot_entry_no')
    )

def downgrade():
    op.drop_table('LotRejectWork')

