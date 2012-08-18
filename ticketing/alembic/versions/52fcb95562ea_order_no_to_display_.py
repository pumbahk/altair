"""order_no_to_display_order

Revision ID: 52fcb95562ea
Revises: 21b64604e7cf
Create Date: 2012-08-19 04:00:25.658349

"""

# revision identifiers, used by Alembic.
revision = '52fcb95562ea'
down_revision = '21b64604e7cf'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('StockType', 'order_no', nullable=False, name='display_order', existing_type=sa.Integer(), existing_server_default='1')
    op.alter_column('Product', 'order_no', nullable=False, name='display_order', existing_type=sa.Integer(), existing_server_default='1')

def downgrade():
    op.alter_column('StockType', 'display_order', nullable=False, name='order_no', existing_type=sa.Integer(), existing_server_default='1')
    op.alter_column('Product', 'display_order', nullable=False, name='order_no', existing_type=sa.Integer(), existing_server_default='1')
