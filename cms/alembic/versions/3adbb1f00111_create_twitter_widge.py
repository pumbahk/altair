"""create twitter widget

Revision ID: 3adbb1f00111
Revises: 170847cf5bb5
Create Date: 2012-06-11 11:26:50.841035

"""

# revision identifiers, used by Alembic.
revision = '3adbb1f00111'
down_revision = '170847cf5bb5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('widget_twitter',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('search_query', sa.Unicode(length=255), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('subject', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_twitter_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table("widget_twitter")
