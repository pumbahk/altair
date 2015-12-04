"""add_member_identifier_to_membership

Revision ID: 13cc3341b9d5
Revises: 42ce654e9a53
Create Date: 2015-11-06 16:16:08.556498

"""

# revision identifiers, used by Alembic.
revision = '13cc3341b9d5'
down_revision = '42ce654e9a53'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Membership', sa.Column('membership_identifier', sa.Unicode(64), nullable=True))

def downgrade():
    op.drop_column('Membership', 'membership_identifier')
