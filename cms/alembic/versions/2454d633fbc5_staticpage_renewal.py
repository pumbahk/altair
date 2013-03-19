"""staticpage renewal

Revision ID: 2454d633fbc5
Revises: 1b9d18c1e5b1
Create Date: 2013-03-18 15:39:12.150935

"""

# revision identifiers, used by Alembic.
revision = '2454d633fbc5'
down_revision = '1b9d18c1e5b1'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('static_pages', sa.Column('publish_end', sa.DateTime(), nullable=True))
    op.add_column('static_pages', sa.Column('layout_id', sa.Integer(), nullable=True))
    op.add_column('static_pages', sa.Column('publish_begin', sa.DateTime(), nullable=True))
    op.create_foreign_key("fk_static_pages_to_layout",  "static_pages", "layout", ["layout_id"], ["id"])

def downgrade():
    op.drop_constraint("fk_static_pages_to_layout", "static_pages", type="foreignkey")
    op.drop_column('static_pages', 'publish_begin')
    op.drop_column('static_pages', 'layout_id')
    op.drop_column('static_pages', 'publish_end')
