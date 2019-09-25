"""Adds time type columns to PaymentDeliveryMethodPair

Revision ID: 3b25f0dfa9a2
Revises: 5453b8be0ac
Create Date: 2019-03-18 16:55:31.930764

"""

# revision identifiers, used by Alembic.
revision = '3b25f0dfa9a2'
down_revision = '5453b8be0ac'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.add_column(table_name='PaymentDeliveryMethodPair',
                  column=sa.Column('payment_period_time', sa.Time(), nullable=True, server_default=text('235900')))
    op.add_column(table_name='PaymentDeliveryMethodPair',
                  column=sa.Column('issuing_interval_time', sa.Time(), nullable=True, server_default=text('000000')))
    op.add_column(table_name='PaymentDeliveryMethodPair',
                  column=sa.Column('issuing_end_in_time', sa.Time(), nullable=True, server_default=text('235900')))


def downgrade():
    op.drop_column(table_name='PaymentDeliveryMethodPair', column_name='payment_period_time')
    op.drop_column(table_name='PaymentDeliveryMethodPair', column_name='issuing_interval_time')
    op.drop_column(table_name='PaymentDeliveryMethodPair', column_name='issuing_end_in_time')
