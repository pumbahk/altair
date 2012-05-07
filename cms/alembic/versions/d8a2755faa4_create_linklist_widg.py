"""create linklist widget

Revision ID: d8a2755faa4
Revises: 18c8a8c86e2d
Create Date: 2012-05-01 14:43:49.355596

"""

# revision identifiers, used by Alembic.
revision = 'd8a2755faa4'
down_revision = '18c8a8c86e2d'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('widget_linklist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column("max_items", sa.Integer()), 
                    sa.Column("finder_kind", sa.Unicode(length=32), nullable=False), 
                    sa.Column("delimiter", sa.Unicode(length=255), nullable=False), 
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table("widget_linklist")

