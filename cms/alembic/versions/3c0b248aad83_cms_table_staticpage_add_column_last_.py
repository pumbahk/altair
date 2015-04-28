"""cms table StaticPage add column last_editor

Revision ID: 3c0b248aad83
Revises: 1dac597a3e70
Create Date: 2015-04-23 17:15:27.336837

"""

# revision identifiers, used by Alembic.
revision = '3c0b248aad83'
down_revision = '1dac597a3e70'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('static_pages', sa.Column('last_editor', sa.String(255)))

def downgrade():
    op.drop_column('static_pages', 'last_editor')
