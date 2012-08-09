"""alter table productitem drop column item_type

Revision ID: 204f9f0af05a
Revises: 297a875d82ea
Create Date: 2012-08-09 19:05:36.031544

"""

# revision identifiers, used by Alembic.
revision = '204f9f0af05a'
down_revision = '297a875d82ea'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.drop_column('ProductItem', 'item_type') 

def downgrade():
    op.add_column('ProductItem', sa.Column('item_type', sa.Integer()))

