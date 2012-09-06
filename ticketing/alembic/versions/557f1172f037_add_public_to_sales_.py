"""add_public_to_sales_segment

Revision ID: 557f1172f037
Revises: 2118ba6ee220
Create Date: 2012-09-06 20:05:44.243508

"""

# revision identifiers, used by Alembic.
revision = '557f1172f037'
down_revision = '2118ba6ee220'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegment', sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')))
    pass

def downgrade():
    op.drop_column('SalesSegment', 'public')
