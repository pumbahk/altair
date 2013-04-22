"""alter table page_default_info add column title_suffix

Revision ID: 1cfa3148b744
Revises: 1bc2fb89c9df
Create Date: 2013-04-22 16:38:35.252563

"""

# revision identifiers, used by Alembic.
revision = '1cfa3148b744'
down_revision = '1bc2fb89c9df'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('page_default_info', sa.Column('title_suffix', sa.UnicodeText(), nullable=True))

def downgrade():
    op.drop_column('page_default_info', 'title_suffix')
