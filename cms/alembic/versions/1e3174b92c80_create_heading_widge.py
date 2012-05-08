"""create heading widget

Revision ID: 1e3174b92c80
Revises: d8a2755faa4
Create Date: 2012-05-01 16:16:28.465367

"""

# revision identifiers, used by Alembic.
revision = '1e3174b92c80'
down_revision = 'd8a2755faa4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('widget_heading',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.Unicode(length=255), nullable=True),
                    sa.Column('text', sa.Unicode(length=255), nullable=True),
                    sa.Column("kind", sa.String(length=32), nullable=False), 
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_heading_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.execute("ALTER TABLE widget_heading DROP FOREIGN KEY fk_widget_heading_id")
    op.drop_table("widget_heading")
