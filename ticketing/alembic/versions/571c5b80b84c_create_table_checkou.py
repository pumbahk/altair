"""create table Checkout

Revision ID: 571c5b80b84c
Revises: 2673bcbc0dca
Create Date: 2012-12-12 20:14:48.137599

"""

# revision identifiers, used by Alembic.
revision = '571c5b80b84c'
down_revision = '2673bcbc0dca'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('Checkout',
        sa.Column('id', Identifier, nullable=False),
        sa.Column('orderId', sa.Unicode(length=30), nullable=True),
        sa.Column('orderControlId', sa.Unicode(length=31), nullable=True),
        sa.Column('orderCartId', sa.Unicode(length=255), nullable=True),
        sa.Column('openId', sa.Unicode(length=128), nullable=True),
        sa.Column('isTMode', sa.Enum('0', '1'), nullable=True),
        sa.Column('usedPoint', sa.Integer(), nullable=True),
        sa.Column('orderTotalFee', sa.Integer(), nullable=True),
        sa.Column('orderDate', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.CheckConstraint('TODO'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('CheckoutItem',
        sa.Column('id', Identifier, nullable=False),
        sa.Column('checkout_id', Identifier, nullable=True),
        sa.Column('itemId', sa.String(length=100), nullable=True),
        sa.Column('itemName', sa.Unicode(length=255), nullable=True),
        sa.Column('itemNumbers', sa.Integer(), nullable=True),
        sa.Column('itemFee', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['checkout_id'], ['Checkout.id'], 'CheckoutItem_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    op.drop_table('CheckoutItem')
    op.drop_table('Checkout')

