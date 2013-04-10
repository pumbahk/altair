"""html attributes movie, flash

Revision ID: 151de63d5dd4
Revises: fb4ae35353d
Create Date: 2013-04-09 11:11:43.292312

"""

# revision identifiers, used by Alembic.
revision = '151de63d5dd4'
down_revision = 'fb4ae35353d'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_movie', sa.Column('attributes', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_flash', sa.Column('attributes', sa.Unicode(length=255), nullable=True))


def downgrade():
    op.drop_column('widget_movie', 'attributes')
    op.drop_column('widget_flash', 'attributes')
