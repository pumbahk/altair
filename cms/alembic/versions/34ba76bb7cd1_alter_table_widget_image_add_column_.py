"""alter table widget_image add column disable_right_click

Revision ID: 34ba76bb7cd1
Revises: 4014a4a8f80e
Create Date: 2014-07-07 10:32:51.846887

"""

# revision identifiers, used by Alembic.
revision = '34ba76bb7cd1'
down_revision = '182156cb4a07'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

def upgrade():
    op.add_column('widget_image', sa.Column('disable_right_click', sa.Boolean(), nullable=False,default=False, server_default=text('0')))

def downgrade():
    op.drop_column('widget_image', 'disable_right_click')
