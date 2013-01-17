"""add_sales_segment_group_id_to_cart

Revision ID: 318a9106a15b
Revises: 50786ebea789
Create Date: 2013-01-17 22:25:28.213844

"""

# revision identifiers, used by Alembic.
revision = '318a9106a15b'
down_revision = '50786ebea789'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Cart', sa.Column('sales_segment_group_id', Identifier(), nullable=True))
    op.create_foreign_key(
        name='Cart_ibfk_6',
        source='Cart',
        referent='SalesSegmentGroup',
        local_cols=['sales_segment_group_id'],
        remote_cols=['id'],
        onupdate='NO ACTION',
        ondelete='NO ACTION'
        )

def downgrade():
    op.drop_constraint('Cart_ibfk_6', 'Cart', 'foreignkey')
    op.drop_column('Cart', 'sales_segment_group_id')
