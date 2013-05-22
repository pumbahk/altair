"""static page have uploaded_at

Revision ID: 4df15f221e78
Revises: 1ac7a5654384
Create Date: 2013-05-21 20:00:40.159441

"""

# revision identifiers, used by Alembic.
revision = '4df15f221e78'
down_revision = '1ac7a5654384'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('static_pages', sa.Column('uploaded_at', sa.DateTime(), nullable=True))
    op.add_column('static_pages', sa.Column('file_structure_text', sa.Text, nullable=False))

def downgrade():
    op.drop_column('static_pages', 'uploaded_at')
    op.drop_column('static_pages', 'file_structure_text')

