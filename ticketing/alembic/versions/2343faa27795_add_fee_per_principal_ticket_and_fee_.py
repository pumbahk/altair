"""add_fee_per_principal_ticket_and_fee_per_subticket_to_delivery_method_and_pdmp

Revision ID: 2343faa27795
Revises: 48b361955fed
Create Date: 2014-07-03 22:42:24.528955

"""

# revision identifiers, used by Alembic.
revision = '2343faa27795'
down_revision = '48b361955fed'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('DeliveryMethod', 'fee', nullable=True, existing_type=sa.Numeric(precision=16, scale=2))
    op.alter_column('DeliveryMethod', 'fee_type', nullable=True, existing_type=sa.Integer(), existing_server_default=sa.text('0'))
    op.add_column('DeliveryMethod', sa.Column('fee_per_order', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.add_column('DeliveryMethod', sa.Column('fee_per_principal_ticket', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.add_column('DeliveryMethod', sa.Column('fee_per_subticket', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.execute('UPDATE DeliveryMethod SET fee_per_order=IF(fee_type=0, fee, 0), fee_per_principal_ticket=IF(fee_type=1, fee, 0), fee_per_subticket=0')
    op.alter_column('PaymentDeliveryMethodPair', 'delivery_fee', nullable=True, existing_type=sa.Numeric(precision=16, scale=2))
    op.add_column('PaymentDeliveryMethodPair', sa.Column('delivery_fee_per_order', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.add_column('PaymentDeliveryMethodPair', sa.Column('delivery_fee_per_principal_ticket', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.add_column('PaymentDeliveryMethodPair', sa.Column('delivery_fee_per_subticket', sa.Numeric(precision=16, scale=2), nullable=False, server_default=sa.text('0.00')))
    op.execute('UPDATE PaymentDeliveryMethodPair JOIN DeliveryMethod ON PaymentDeliveryMethodPair.delivery_method_id=DeliveryMethod.id SET delivery_fee_per_order=IF(fee_type=0, fee, 0), delivery_fee_per_principal_ticket=IF(fee_type=1, fee, 0), delivery_fee_per_subticket=0')

def downgrade():
    op.alter_column('DeliveryMethod', 'fee', nullable=False, existing_type=sa.Numeric(precision=16, scale=2))
    op.alter_column('DeliveryMethod', 'fee_type', nullable=False, existing_type=sa.Integer(), existing_server_default=sa.text('0'))
    op.alter_column('PaymentDeliveryMethodPair', 'delivery_fee', nullable=False, existing_type=sa.Numeric(precision=16, scale=2))
    op.drop_column('DeliveryMethod', 'fee_per_order')
    op.drop_column('DeliveryMethod', 'fee_per_principal_ticket')
    op.drop_column('DeliveryMethod', 'fee_per_subticket')
    op.drop_column('PaymentDeliveryMethodPair', 'delivery_fee_per_order')
    op.drop_column('PaymentDeliveryMethodPair', 'delivery_fee_per_principal_ticket')
    op.drop_column('PaymentDeliveryMethodPair', 'delivery_fee_per_subticket')
