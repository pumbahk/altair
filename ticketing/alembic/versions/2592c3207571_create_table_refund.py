"""create table Refund

Revision ID: 2592c3207571
Revises: 1f92f73d0a7e
Create Date: 2013-02-04 15:19:18.600808

"""

# revision identifiers, used by Alembic.
revision = '2592c3207571'
down_revision = '1f92f73d0a7e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('Refund',
        sa.Column('id', Identifier, nullable=False),
        sa.Column('payment_method_id', Identifier, nullable=True),
        sa.Column('include_fee', sa.Boolean, nullable=False, default=False),
        sa.Column('include_item', sa.Boolean, nullable=False, default=False),
        sa.Column('reason', sa.String(255), nullable=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['payment_method_id'], ['PaymentMethod.id'], 'Refund_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )
    op.create_table('Refund_Order',
        sa.Column('refund_id', Identifier, nullable=False),
        sa.Column('order_no', sa.String(255), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['refund_id'], ['Refund.id'], 'Refund_Order_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_no'], ['Order.order_no'], 'Refund_Order_ibfk_2', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('refund_id', 'order_no')
        )

def downgrade():
    op.drop_table('Refund_Order')
    op.drop_table('Refund')

