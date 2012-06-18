"""add column genre linklist

Revision ID: 4019ba1e72e1
Revises: 49bdc26db52e
Create Date: 2012-06-18 17:47:39.214066

"""

# revision identifiers, used by Alembic.
revision = '4019ba1e72e1'
down_revision = '49bdc26db52e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('widget_linklist', sa.Column('genre', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('widget_linklist', 'genre')
