"""PDMP <-> SalesSegment

Revision ID: 47f92d43c86d
Revises: 398b8a0974eb
Create Date: 2013-01-27 12:57:39.836764

"""

# revision identifiers, used by Alembic.
revision = '47f92d43c86d'
down_revision = '398b8a0974eb'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
    "SalesSegment_PaymentDeliveryMethodPair",
    sa.Column('id', Identifier, primary_key=True),
    sa.Column('payment_delivery_method_pair', Identifier, sa.ForeignKey('PaymentDeliveryMethodPair.id')),
    sa.Column('sales_segment_id', Identifier, sa.ForeignKey('SalesSegment.id')),
    )

def downgrade():
    op.drop_table(
    "SalesSegment_PaymentDeliveryMethodPair",
    )
