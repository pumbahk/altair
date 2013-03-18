"""alter table Event add column cms_send_at

Revision ID: 9b32b7c8d35
Revises: 17d62e30cb0d
Create Date: 2013-03-15 15:12:52.217227

"""

# revision identifiers, used by Alembic.
revision = '9b32b7c8d35'
down_revision = '17d62e30cb0d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Event', sa.Column('cms_send_at', sa.TIMESTAMP(), nullable=True, default=None))

def downgrade():
    op.drop_column('Event', 'cms_send_at')
