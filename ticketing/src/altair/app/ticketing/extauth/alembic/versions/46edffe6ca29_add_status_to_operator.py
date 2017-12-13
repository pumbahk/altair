"""add status to operator

Revision ID: 46edffe6ca29
Revises: 14247fb69ba6
Create Date: 2017-12-06 20:28:29.741590

"""

# revision identifiers, used by Alembic.
revision = '46edffe6ca29'
down_revision = '14247fb69ba6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Operator', sa.Column('status', sa.Integer, server_default=('1')))
    op.add_column('Operator', sa.Column('expired_at', sa.DateTime))
    op.execute("UPDATE Operator SET expired_at = (created_at + INTERVAL  180 DAY);")

def downgrade():
    op.drop_column('Operator', 'expired_at')
    op.drop_column('Operator', 'status')
