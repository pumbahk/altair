"""topcontent has rendering_image_attribute

Revision ID: 3ec39db2a88
Revises: 2af18a487a43
Create Date: 2013-03-22 20:08:10.600334

"""

# revision identifiers, used by Alembic.
revision = '3ec39db2a88'
down_revision = '2af18a487a43'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('widget_topcontent', sa.Column('rendering_image_attribute', sa.String(length=16), nullable=False))
    op.execute('update widget_topcontent set rendering_image_attribute = "thumbnail_path";')

def downgrade():
    op.drop_column('widget_topcontent', 'rendering_image_attribute')
