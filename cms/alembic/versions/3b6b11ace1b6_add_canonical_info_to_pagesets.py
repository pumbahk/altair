"""add canonical info to pagesets

Revision ID: 3b6b11ace1b6
Revises: cb8ec766437
Create Date: 2017-08-29 13:41:59.847991

"""

# revision identifiers, used by Alembic.
revision = '3b6b11ace1b6'
down_revision = 'cb8ec766437'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'pagesets', sa.Column('canonical_url', sa.Unicode(length=255), nullable=True))
    op.add_column(u'pagesets', sa.Column('canonical_redirect', sa.Boolean, server_default=('0')))

def downgrade():
    op.drop_column(u'pagesets', 'canonical_url')
    op.drop_column(u'pagesets', 'canonical_redirect')