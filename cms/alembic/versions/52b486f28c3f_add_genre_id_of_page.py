"""add genre_id of pagesets

Revision ID: 52b486f28c3f
Revises: 406f55ec156e
Create Date: 2013-02-13 10:54:26.241075

"""

# revision identifiers, used by Alembic.
revision = '52b486f28c3f'
down_revision = '406f55ec156e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('pagesets', sa.Column('genre_id', sa.Integer(), nullable=True))
    op.add_column('genre', sa.Column('is_root', sa.Boolean(), nullable=False, default=True))
    op.add_column('genre', sa.Column('display_order', sa.Boolean(), default=50))
    op.add_column('widget_topic', sa.Column('system_tag_id', sa.Integer()))
    op.create_foreign_key("widget_topoic_ibfk_2", "widget_topic", "topiccoretag", ["system_tag_id"], ["id"])

def downgrade():
    op.drop_constraint("widget_topoic_ibfk_2", "widget_topic", type="foreignkey")
    op.drop_column("widget_topic", "system_tag_id")
    op.drop_column('pagesets', 'genre_id')
    op.drop_column('genre', 'is_root')
    op.drop_column('genre', 'display_order')


