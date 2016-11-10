"""add_genre_id_to_static_page

Revision ID: 5649c3858eb1
Revises: 4d76c7847d67
Create Date: 2016-11-01 18:54:23.393707

"""

# revision identifiers, used by Alembic.
revision = '5649c3858eb1'
down_revision = '4d76c7847d67'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'static_pagesets', sa.Column('genre_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column(u'static_pagesets', 'genre_id')
