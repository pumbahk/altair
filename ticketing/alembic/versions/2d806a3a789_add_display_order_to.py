"""add_display_order_to_performance

Revision ID: 2d806a3a789
Revises: 6ee82086f5a
Create Date: 2013-07-12 15:03:58.409328

"""

# revision identifiers, used by Alembic.
revision = '2d806a3a789'
down_revision = '6ee82086f5a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Performance', sa.Column('display_order', sa.Integer(), nullable=False, default=1, server_default=text('1')))

def downgrade():
    op.drop_column('Performance', 'display_order')
