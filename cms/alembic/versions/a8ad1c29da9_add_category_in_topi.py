"""add subkind in topic topic widget

Revision ID: a8ad1c29da9
Revises: 152b9d4cf2a4
Create Date: 2012-05-07 19:48:28.961564

"""

# revision identifiers, used by Alembic.
revision = 'a8ad1c29da9'
down_revision = '152b9d4cf2a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('topic',
                  sa.Column('subkind', sa.Unicode(length=255), nullable=True))
    op.add_column('topcontent',
                  sa.Column('subkind', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_topic',
                  sa.Column('subkind', sa.Unicode(length=255), nullable=True))


def downgrade():
    op.drop_column("topic", "subkind")
    op.drop_column("topcontent", "subkind")
    op.drop_column("widget_topic", "subkind")
