"""add resale performance_id to resalesegment

Revision ID: 3f34af8d2a26
Revises: 13151cb706a
Create Date: 2018-05-14 12:01:41.278473

"""

# revision identifiers, used by Alembic.
revision = '3f34af8d2a26'
down_revision = '13151cb706a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ResaleSegment', sa.Column('resale_performance_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column('ResaleSegment', 'resale_performance_id')
