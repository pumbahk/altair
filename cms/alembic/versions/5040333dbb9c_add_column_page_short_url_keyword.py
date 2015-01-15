"""empty message

Revision ID: 5040333dbb9c
Revises: 36996b42119b
Create Date: 2014-12-25 15:52:10.178573

"""

# revision identifiers, used by Alembic.
revision = '5040333dbb9c'
down_revision = '36996b42119b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('page', sa.Column('short_url_keyword', sa.String(255), default=None))

def downgrade():
    op.drop_column('page', 'short_url_keyword')
