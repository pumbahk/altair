"""add_flags_to_ticket

Revision ID: 2655d4d39145
Revises: 1adad219947d
Create Date: 2012-09-07 12:23:37.720420

"""

# revision identifiers, used by Alembic.
revision = '2655d4d39145'
down_revision = '1adad219947d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Ticket', sa.Column('flags', sa.Integer(), nullable=False, default=0, server_default=text('0')))

def downgrade():
    op.drop_column('Ticket', 'flags')
