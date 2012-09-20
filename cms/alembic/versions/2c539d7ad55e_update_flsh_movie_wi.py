"""update flsh, movie widget

Revision ID: 2c539d7ad55e
Revises: 1f20b26aaa74
Create Date: 2012-09-20 14:14:33.521377

"""

# revision identifiers, used by Alembic.
revision = '2c539d7ad55e'
down_revision = '1f20b26aaa74'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('widget_flash', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('widget_flash', sa.Column('alt', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_flash', sa.Column('href', sa.String(length=255), nullable=True))
    op.add_column('widget_flash', sa.Column('height', sa.Integer(), nullable=True))

    op.add_column('widget_movie', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('widget_movie', sa.Column('alt', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_movie', sa.Column('href', sa.String(length=255), nullable=True))
    op.add_column('widget_movie', sa.Column('height', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('widget_flash', 'height')
    op.drop_column('widget_flash', 'href')
    op.drop_column('widget_flash', 'alt')
    op.drop_column('widget_flash', 'width')

    op.drop_column('widget_movie', 'height')
    op.drop_column('widget_movie', 'href')
    op.drop_column('widget_movie', 'alt')
    op.drop_column('widget_movie', 'width')
