"""create iconset widget

Revision ID: 18c8a8c86e2d
Revises: 398be24dc7ed
Create Date: 2012-04-27 12:04:16.802163

"""

# revision identifiers, used by Alembic.
revision = '18c8a8c86e2d'
down_revision = '398be24dc7ed'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('widget_iconset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.Unicode(length=255), nullable=True),
                    sa.Column("kind", sa.String(length=32), nullable=False), 
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_iconset_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.execute("ALTER TABLE widget_iconset DROP FOREIGN KEY fk_widget_iconset_widget_id")
    op.drop_table("widget_iconset")
