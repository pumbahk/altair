"""add Host.mobile_base_url

Revision ID: 48451f969768
Revises: 318a9106a15b
Create Date: 2013-01-18 13:58:46.225607

"""

# revision identifiers, used by Alembic.
revision = '48451f969768'
down_revision = '318a9106a15b'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('Host', sa.Column('mobile_base_url', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('Host', 'mobile_base_url')
