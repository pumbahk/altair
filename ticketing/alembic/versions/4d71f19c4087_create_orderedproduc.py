"""create OrderedProductItemToken

Revision ID: 4d71f19c4087
Revises: 825b50ada09
Create Date: 2012-09-14 14:15:40.629651

"""

# revision identifiers, used by Alembic.
revision = '4d71f19c4087'
down_revision = '825b50ada09'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('OrderedProductItemToken',
    sa.Column('id', Identifier, nullable=False),
    sa.Column('ordered_product_item_id', Identifier, nullable=False),
    sa.Column('seat_id', Identifier, nullable=True),
    sa.Column('serial', sa.Integer(), nullable=False),
    sa.Column('key', sa.Unicode(length=255), nullable=True),
    sa.Column('valid', sa.Boolean(), nullable=False),
    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
    sa.ForeignKeyConstraint(['ordered_product_item_id'], ['OrderedProductItem.id'],
                            "OrderedProductItemToken_ibfk_1", ondelete="CASCADE"),
    sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 
                            "OrderedProductItemToken_ibfk_2", ondelete="CASCADE"),
    sa.PrimaryKeyConstraint('id')
    )

def downgrade():
    op.drop_constraint('OrderedProductItemToken_ibfk_1', 'OrderedProductItemToken', type='foreignkey')
    op.drop_constraint('OrderedProductItemToken_ibfk_2', 'OrderedProductItemToken', type='foreignkey')
    op.drop_table("OrderedProductItemToken")

