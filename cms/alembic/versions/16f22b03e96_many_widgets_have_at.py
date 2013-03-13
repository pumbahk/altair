"""many widgets have attributes field

Revision ID: 16f22b03e96
Revises: 1ac1e1ebe04a
Create Date: 2013-03-12 16:58:42.473865

"""

# revision identifiers, used by Alembic.
revision = '16f22b03e96'
down_revision = '1ac1e1ebe04a'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('widget_image', sa.Column('attributes', sa.Unicode(length=255), nullable=True))
    op.add_column('widget_purchase', sa.Column('attributes', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('widget_purchase', 'attributes')
    op.drop_column('widget_image', 'attributes')
