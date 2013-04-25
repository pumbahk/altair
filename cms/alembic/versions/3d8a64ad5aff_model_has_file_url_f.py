"""model has file_url (for s3)

Revision ID: 3d8a64ad5aff
Revises: 1cfa3148b744
Create Date: 2013-04-23 20:20:52.829292

"""

# revision identifiers, used by Alembic.
revision = '3d8a64ad5aff'
down_revision = '1cfa3148b744'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('flash_asset', sa.Column('thumbnail_url', sa.String(length=255), nullable=True))
    op.add_column('flash_asset', sa.Column('file_url', sa.String(length=255), nullable=True))
    op.add_column('image_asset', sa.Column('thumbnail_url', sa.String(length=255), nullable=True))
    op.add_column('image_asset', sa.Column('file_url', sa.String(length=255), nullable=True))
    op.add_column('movie_asset', sa.Column('thumbnail_url', sa.String(length=255), nullable=True))
    op.add_column('movie_asset', sa.Column('file_url', sa.String(length=255), nullable=True))
    op.add_column('flash_asset', sa.Column('thumbnail_url', sa.String(length=255), nullable=True))
    op.add_column('flash_asset', sa.Column('file_url', sa.String(length=255), nullable=True))
    op.add_column('layout', sa.Column('file_url', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('movie_asset', 'file_url')
    op.drop_column('movie_asset', 'thumbnail_url')
    op.drop_column('layout', 'file_url')
    op.drop_column('image_asset', 'file_url')
    op.drop_column('image_asset', 'thumbnail_url')
    op.drop_column('flash_asset', 'file_url')
    op.drop_column('flash_asset', 'thumbnail_url')
