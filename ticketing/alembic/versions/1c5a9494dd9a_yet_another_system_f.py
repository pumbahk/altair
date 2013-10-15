"""yet another system fee

Revision ID: 1c5a9494dd9a
Revises: 4ca796782d0a
Create Date: 2013-10-01 18:27:54.768122

"""

# revision identifiers, used by Alembic.
revision = '1c5a9494dd9a'
down_revision = '4e6dd834d693'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('PaymentDeliveryMethodPair',
                  sa.Column('special_fee_name',
                            sa.String(length=255), nullable=False, default=""))
    op.add_column('PaymentDeliveryMethodPair',
                  sa.Column('special_fee',
                            sa.Integer(), nullable=False, default=0))
    op.add_column('PaymentDeliveryMethodPair',
                  sa.Column('special_fee_type',
                            sa.Integer(), nullable=False, default=0))

    op.add_column('Order',
                  sa.Column('special_fee_name',
                            sa.String(length=255), nullable=False, default=""))
    op.add_column('Order',
                  sa.Column('special_fee',
                            sa.Integer(), nullable=False, default=0))
    op.add_column('Refund',
                  sa.Column('include_special_fee',
                            sa.Boolean(), nullable=False, default=False))

def downgrade():
    op.drop_column('PaymentDeliveryMethodPair', 'special_fee_name')
    op.drop_column('PaymentDeliveryMethodPair', 'special_fee')
    op.drop_column('PaymentDeliveryMethodPair', 'special_fee_type')
    op.drop_column('Order', 'special_fee_name')
    op.drop_column('Order', 'special_fee')
    op.drop_column('Refund', 'include_special_fee')
