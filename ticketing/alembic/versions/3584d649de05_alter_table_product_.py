"""alter table product_item add column name

Revision ID: 3584d649de05
Revises: c53469fce5
Create Date: 2012-08-14 16:19:45.462014

"""

# revision identifiers, used by Alembic.
revision = '3584d649de05'
down_revision = 'c53469fce5'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('ProductItem', sa.Column('name', sa.String(255)))

def downgrade():
    op.drop_column('ProductItem', 'name') 

