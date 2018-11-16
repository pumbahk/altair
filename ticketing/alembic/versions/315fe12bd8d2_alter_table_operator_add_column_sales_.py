"""alter table Operator add column sales_seach

Revision ID: 315fe12bd8d2
Revises: 3f8810964ed2
Create Date: 2018-11-16 10:45:12.976026

"""

# revision identifiers, used by Alembic.
revision = '315fe12bd8d2'
down_revision = '3f8810964ed2'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Operator',
                  sa.Column('sales_search', sa.Boolean(), nullable=False, default=False, server_default=text('0')))


def downgrade():
    op.drop_column('Operator', 'sales_search')
