"""add_cancellation_scheduled_at_to_multicheckout_order_status

Revision ID: 7657f6f6b68
Revises: 1f3bf8e6fd46
Create Date: 2014-12-15 00:33:45.611730

"""

# revision identifiers, used by Alembic.
revision = '7657f6f6b68'
down_revision = '1f3bf8e6fd46'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('multicheckout_order_status', sa.Column('CancellationScheduledAt', sa.DateTime(), nullable=True))
    op.add_column('multicheckout_order_status', sa.Column('EventualSalesAmount', sa.Integer(), nullable=True))
    op.add_column('multicheckout_order_status', sa.Column('TaxCarriageAmountToCancel', sa.Integer(), nullable=True))

def downgrade():
    op.drop_column('multicheckout_order_status', 'CancellationScheduledAt')
    op.drop_column('multicheckout_order_status', 'EventualSalesAmount')
    op.drop_column('multicheckout_order_status', 'TaxCarriageAmountToCancel')
