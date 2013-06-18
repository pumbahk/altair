"""static page has interceptive

Revision ID: 206025bc6041
Revises: 3ec39db2a88
Create Date: 2013-03-22 20:47:35.617686

"""

# revision identifiers, used by Alembic.
revision = '206025bc6041'
down_revision = '3ec39db2a88'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('static_pages', sa.Column('interceptive', sa.Boolean(), nullable=True))
    op.execute("update static_pages set interceptive = 1;")

def downgrade():
    op.drop_column('static_pages', 'interceptive')
