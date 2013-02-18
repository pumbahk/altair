"""add static_page.published

Revision ID: 95ae1226efe
Revises: 2ad0f44f5142
Create Date: 2013-02-18 16:36:13.214431

"""

# revision identifiers, used by Alembic.
revision = '95ae1226efe'
down_revision = '2ad0f44f5142'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('static_pages', sa.Column('published', sa.Boolean(), nullable=False, default=False))

def downgrade():
    op.drop_column('static_pages', 'published')
