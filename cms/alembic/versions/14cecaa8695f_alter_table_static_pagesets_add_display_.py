"""alter table static_pagesets add display_order

Revision ID: 14cecaa8695f
Revises: 3b6b11ace1b6
Create Date: 2018-06-05 18:38:58.280304

"""

# revision identifiers, used by Alembic.
revision = '14cecaa8695f'
down_revision = '3b6b11ace1b6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('static_pagesets', sa.Column('display_order', sa.Integer(), nullable=False))


def downgrade():
    op.drop_column('static_pagesets', 'display_order')
