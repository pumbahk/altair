"""alter table product add column orderno

Revision ID: 120a39674247
Revises: 260f594c554f
Create Date: 2012-08-09 21:51:23.194802

"""

# revision identifiers, used by Alembic.
revision = '120a39674247'
down_revision = '260f594c554f'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('Product', sa.Column('order_no', sa.Integer(), default=1))

def downgrade():
    op.drop_column('Product', 'order_no') 

