"""add thumbnail_path image asset

Revision ID: 5a8a6eccba80
Revises: 2ad0f44f5142
Create Date: 2013-01-25 11:50:35.747930

"""

# revision identifiers, used by Alembic.
revision = '5a8a6eccba80'
down_revision = '2ad0f44f5142'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.alter_column('category', u'attributes',
                    existing_type=mysql.VARCHAR(length=255),
                    nullable=True)
    op.add_column('flash_asset', sa.Column('thumbnail_path', sa.String(length=255), nullable=True))
    op.add_column('image_asset', sa.Column('thumbnail_path', sa.String(length=255), nullable=True))
    op.add_column('movie_asset', sa.Column('thumbnail_path', sa.String(length=255), nullable=True))
    op.drop_column('flash_asset', u'imagepath')
    op.drop_column('movie_asset', u'imagepath')

def downgrade():
    op.add_column('movie_asset', sa.Column(u'imagepath', mysql.VARCHAR(length=255), nullable=True))
    op.add_column('flash_asset', sa.Column(u'imagepath', mysql.VARCHAR(length=255), nullable=True))
    op.drop_column('movie_asset', 'thumbnail_path')
    op.drop_column('image_asset', 'thumbnail_path')
    op.drop_column('flash_asset', 'thumbnail_path')
