"""LotEntryAttribute

Revision ID: 34ecd9a19da2
Revises: 30afb058c47
Create Date: 2015-01-14 04:33:06.200232

"""

# revision identifiers, used by Alembic.
revision = '34ecd9a19da2'
down_revision = '482f7ef338d1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'LotEntryAttribute',
        sa.Column('lot_entry_id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('value', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['lot_entry_id'], ['LotEntry.id'],
                                name='LotEntryAttribute_ibfk_1'),
        sa.PrimaryKeyConstraint('lot_entry_id', 'name')
        )


def downgrade():
    op.drop_table('LotEntryAttribute')
