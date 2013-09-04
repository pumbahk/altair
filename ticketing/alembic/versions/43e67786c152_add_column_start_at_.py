"""add column start_at, end_at on Refund

Revision ID: 43e67786c152
Revises: 53af2f49cb08
Create Date: 2013-08-28 12:07:22.453504

"""

# revision identifiers, used by Alembic.
revision = '43e67786c152'
down_revision = '53af2f49cb08'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'Refund', sa.Column('start_at', sa.DateTime(), nullable=False))
    op.add_column(u'Refund', sa.Column('end_at', sa.DateTime(), nullable=False))

def downgrade():
    op.drop_column(u'Refund', 'start_at')
    op.drop_column(u'Refund', 'end_at')
