"""static page has label

Revision ID: fb4ae35353d
Revises: 206025bc6041
Create Date: 2013-03-28 17:19:25.387940

"""

# revision identifiers, used by Alembic.
revision = 'fb4ae35353d'
down_revision = '206025bc6041'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('static_pages', sa.Column('label', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('static_pages', 'label')
