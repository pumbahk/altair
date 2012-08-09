"""alter table stocktype add column orderno

Revision ID: 260f594c554f
Revises: 204f9f0af05a
Create Date: 2012-08-09 20:59:06.631885

"""

# revision identifiers, used by Alembic.
revision = '260f594c554f'
down_revision = '204f9f0af05a'

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('StockType', sa.Column('order_no', sa.Integer(), default=1))

def downgrade():
    op.drop_column('StockType', 'order_no') 

