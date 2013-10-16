"""index on MailSubscription.email

Revision ID: 1b7e3b0480d2
Revises: 587cd54b6dfc
Create Date: 2013-10-16 14:52:37.167251

"""

# revision identifiers, used by Alembic.
revision = '1b7e3b0480d2'
down_revision = '587cd54b6dfc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('email', 'MailSubscription', ['email'])

def downgrade():
    op.drop_index('email', 'MailSubscription')

