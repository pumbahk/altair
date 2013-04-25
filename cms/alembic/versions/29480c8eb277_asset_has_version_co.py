"""asset has version_counter

Revision ID: 29480c8eb277
Revises: 3d8a64ad5aff
Create Date: 2013-04-25 17:30:59.927968

"""

# revision identifiers, used by Alembic.
revision = '29480c8eb277'
down_revision = '3d8a64ad5aff'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('image_asset', sa.Column('version_counter', sa.SmallInteger, nullable=False, default=0))
    op.add_column('movie_asset', sa.Column('version_counter', sa.SmallInteger, nullable=False, default=0))
    op.add_column('flash_asset', sa.Column('version_counter', sa.SmallInteger, nullable=False, default=0))
    op.add_column('layout', sa.Column('version_counter', sa.SmallInteger, nullable=False, default=0))
    op.execute("update image_asset set version_counter = 0;")
    op.execute("update movie_asset set version_counter = 0;")
    op.execute("update flash_asset set version_counter = 0;")
    op.execute("update layout set version_counter = 0;")


def downgrade():
    op.drop_column('image_asset', 'version_counter')
    op.drop_column('movie_asset', 'version_counter')
    op.drop_column('flash_asset', 'version_counter')
    op.drop_column('layout', 'version_counter')
