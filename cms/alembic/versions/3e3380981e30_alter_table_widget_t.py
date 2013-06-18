"""alter table widget_twitter add column data_widget_id

Revision ID: 3e3380981e30
Revises: 106b8f6b5e09
Create Date: 2013-06-12 17:05:57.306383

"""

# revision identifiers, used by Alembic.
revision = '3e3380981e30'
down_revision = '106b8f6b5e09'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_twitter', sa.Column('data_widget_id', sa.Unicode(length=255)))

def downgrade():
    op.drop_column('widget_twitter', 'data_widget_id')
