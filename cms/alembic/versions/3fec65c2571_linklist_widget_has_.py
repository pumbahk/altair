"""linklist widget has system_tag

Revision ID: 3fec65c2571
Revises: 1b9d18c1e5b1
Create Date: 2013-03-21 14:47:25.384262

"""

# revision identifiers, used by Alembic.
revision = '3fec65c2571'
down_revision = '1b9d18c1e5b1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('widget_linklist', sa.Column('system_tag_id', sa.Integer(), nullable=True))
    op.create_foreign_key("fk_widget_linklist_system_tag_to_page", "widget_linklist", "pagetag", ["system_tag_id"], ["id"])
    op.drop_column("widget_linklist", "genre")

def downgrade():
    op.drop_constraint("fk_widget_linklist_system_tag_to_page", "widget_linklist", type="foreignkey")
    op.drop_column('widget_linklist', 'system_tag_id')
    op.add_column("widget_linklist", sa.Column("genre", sa.Unicode(255), nullable=True))
