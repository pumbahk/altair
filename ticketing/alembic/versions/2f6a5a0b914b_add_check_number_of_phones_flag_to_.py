"""add check number of phones flag to OrionPerformance

Revision ID: 2f6a5a0b914b
Revises: 3b6e8e49447a
Create Date: 2018-04-16 13:57:23.707011

"""

# revision identifiers, used by Alembic.
revision = '2f6a5a0b914b'
down_revision = '3b6e8e49447a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrionPerformance', sa.Column('check_number_of_phones', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('OrionPerformance', 'check_number_of_phones')
