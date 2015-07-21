"""create widget_lotsreview table

Revision ID: d82cd501e6b
Revises: d1c7c539d39
Create Date: 2015-07-03 16:13:11.715888

"""

# revision identifiers, used by Alembic.
revision = 'd82cd501e6b'
down_revision = 'd1c7c539d39'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table('widget_lotsreview',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('kind', sa.Unicode(length=32), nullable=True),
        sa.Column('external_link', sa.Unicode(length=255), nullable=True),
        sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_lotsreview_id_to_widget_id"),
        sa.PrimaryKeyConstraint('id'),
        sa.Column('attributes', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_table('widget_lotsreview')
