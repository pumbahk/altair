"""add created_at in pageset

Revision ID: 2a574378e873
Revises: ea688732982
Create Date: 2012-08-07 14:26:58.531966

"""

# revision identifiers, used by Alembic.
revision = '2a574378e873'
down_revision = 'ea688732982'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('pagesets', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('pagesets', sa.Column('updated_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('pagesets', 'updated_at')
    op.drop_column('pagesets', 'created_at')
