"""add_proto_order

Revision ID: 2c6b02262439
Revises: 520345d0d89f
Create Date: 2014-01-16 11:58:35.492605

"""

# revision identifiers, used by Alembic.
revision = '2c6b02262439'
down_revision = '520345d0d89f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ProtoOrder',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('ref', sa.String(length=255), nullable=True),
        sa.Column('order_no', sa.String(length=255), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('operator_id', Identifier(), nullable=True),
        sa.Column('shipping_address_id', Identifier(), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('sales_segment_id', Identifier(), nullable=True),
        sa.Column('total_amount', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('system_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('transaction_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('delivery_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('special_fee', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('special_fee_name', sa.String(length=255), nullable=True),
        sa.Column('payment_delivery_method_pair_id', Identifier(), nullable=True),
        sa.Column('original_order_id', Identifier(), nullable=True),
        sa.Column('original_lot_entry_id', Identifier(), nullable=True),
        sa.Column('order_import_task_id', Identifier(), nullable=True),
        sa.Column('attributes', sa.TEXT(16384), nullable=True, default='{"errors":[]}'),
        sa.Column('issuing_start_at', sa.DateTime(), nullable=True),
        sa.Column('issuing_end_at', sa.DateTime(), nullable=True),
        sa.Column('payment_start_at', sa.DateTime(), nullable=True),
        sa.Column('payment_due_at', sa.DateTime(), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('new_order_paid_at', sa.DateTime(), nullable=True),
        sa.Column('new_order_created_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('note', sa.UnicodeText(), nullable=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.Index('order_no', 'order_no'),
        sa.UniqueConstraint('order_import_task_id', 'order_no'),
        sa.UniqueConstraint('order_import_task_id', 'ref'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'ProtoOrder_ibfk_1'),
        sa.ForeignKeyConstraint(['payment_delivery_method_pair_id'], ['PaymentDeliveryMethodPair.id'], 'ProtoOrder_ibfk_2'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'ProtoOrder_ibfk_3'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], 'ProtoOrder_ibfk_4'),
        sa.ForeignKeyConstraint(['shipping_address_id'], ['ShippingAddress.id'], 'ProtoOrder_ibfk_5'),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'ProtoOrder_ibfk_6'),
        sa.ForeignKeyConstraint(['original_order_id'], ['Order.id'], 'ProtoOrder_ibfk_7', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['original_lot_entry_id'], ['LotEntry.id'], 'ProtoOrder_ibfk_8', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_import_task_id'], ['OrderImportTask.id'], 'ProtoOrder_ibfk_9', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ProtoOrder_ibfk_10'),
        sa.PrimaryKeyConstraint('id')
        )
    op.add_column('OrderedProduct', sa.Column('proto_order_id', Identifier(), nullable=True))
    op.create_foreign_key('OrderedProduct_ibfk_3', 'OrderedProduct', 'ProtoOrder', ['proto_order_id'], ['id'], ondelete='CASCADE')

def downgrade():
    op.drop_constraint('OrderedProduct_ibfk_3', 'OrderedProduct', type_='foreignkey')
    op.drop_column('OrderedProduct', 'proto_order_id')
    op.drop_table('ProtoOrder')
