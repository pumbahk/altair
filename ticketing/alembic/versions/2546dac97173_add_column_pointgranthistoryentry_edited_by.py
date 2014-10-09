"""Add edited_by column and foreign key constraint to PointGrantHistoryEntry

Revision ID: 2546dac97173
Revises: 21b17187ac8a
Create Date: 2014-09-23 15:13:41.064073

"""

# revision identifiers, used by Alembic.
revision = '2546dac97173'
down_revision = '21b17187ac8a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'PointGrantHistoryEntry', sa.Column(u'edited_by', sa.BigInteger, nullable=True, default=None))
    op.create_foreign_key(u'PointGrantHistoryEntry_ibfk_3', 'PointGrantHistoryEntry', 'Operator', ['edited_by'], ['id'])

def downgrade():
    op.drop_constraint('PointGrantHistoryEntry_ibfk_3', 'PointGrantHistoryEntry', 'foreignkey')
    op.drop_column(u'PointGrantHistoryEntry', u'edited_by')
