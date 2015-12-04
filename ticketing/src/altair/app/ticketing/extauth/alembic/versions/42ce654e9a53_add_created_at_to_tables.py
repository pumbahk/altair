"""add_created_at_to_membership

Revision ID: 42ce654e9a53
Revises: 59015d7cef55
Create Date: 2015-10-28 10:29:53.511856

"""

# revision identifiers, used by Alembic.
revision = '42ce654e9a53'
down_revision = '59015d7cef55'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    for table in ['Member', 'Membership', 'OAuthClient']:
        op.add_column(table, sa.Column('created_at', sa.DateTime(), nullable=True, server_default=text(u'CURRENT_TIMESTAMP()')))

def downgrade():
    for table in ['Member', 'Membership', 'OAuthClient']:
        op.drop_column(table, 'created_at')
