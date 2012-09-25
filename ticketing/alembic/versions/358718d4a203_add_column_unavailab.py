"""add column unavailable_period_days

Revision ID: 358718d4a203
Revises: 423bbf5b2949
Create Date: 2012-09-25 16:16:52.189851

"""

# revision identifiers, used by Alembic.
revision = '358718d4a203'
down_revision = '423bbf5b2949'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PaymentDeliveryMethodPair', sa.Column('unavailable_period_days', sa.Integer(), nullable=False, default=0))
    op.add_column('PaymentDeliveryMethodPair', sa.Column('public', sa.Boolean(), nullable=False, default=True, server_default=text('1')))

def downgrade():
    op.drop_column('PaymentDeliveryMethodPair', 'unavailable_period_days') 
    op.drop_column('PaymentDeliveryMethodPair', 'public') 

