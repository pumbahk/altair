"""image widget

Revision ID: 3ed842f1b24c
Revises: 28e9b6af38df
Create Date: 2012-06-15 13:24:06.936297

"""

# revision identifiers, used by Alembic.
revision = '3ed842f1b24c'
down_revision = '28e9b6af38df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('widget_image', sa.Column('width', sa.Integer(), nullable=True))
    op.add_column('widget_image', sa.Column('height', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('widget_image', 'width')
    op.drop_column('widget_image', 'height')
