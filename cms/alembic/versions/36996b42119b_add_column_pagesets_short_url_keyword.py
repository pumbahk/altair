"""empty message

Revision ID: 36996b42119b
Revises: 44cf123e739c
Create Date: 2014-12-25 12:27:59.498294

"""

# revision identifiers, used by Alembic.
revision = '36996b42119b'
down_revision = '44cf123e739c'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pagesets', sa.Column('short_url_keyword', sa.String(255), default=None))

def downgrade():
    op.drop_column('pagesets', 'short_url_keyword')
