"""create anchorlist widget

Revision ID: 49a1b9ae642f
Revises: b5ecfbf167f
Create Date: 2012-05-11 14:48:35.273838

"""

# revision identifiers, used by Alembic.
revision = '49a1b9ae642f'
down_revision = 'b5ecfbf167f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('widget_anchorlist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_anchorlist_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.execute("ALTER TABLE widget_anchorlist DROP FOREIGN KEY fk_widget_anchorlist_widget_id")
    op.drop_table("widget_anchorlist")

