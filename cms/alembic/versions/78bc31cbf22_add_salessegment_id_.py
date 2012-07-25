"""add salessegment id calendar widget

Revision ID: 78bc31cbf22
Revises: 56562d554dfe
Create Date: 2012-07-24 16:17:23.346901

"""

# revision identifiers, used by Alembic.
revision = '78bc31cbf22'
down_revision = '56562d554dfe'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('widget_calendar', sa.Column('salessegment_id', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('widget_calendar', 'salessegment_id')
