"""add_indexes_to_shipping_address

Revision ID: 2878cafe175e
Revises: 38c552ae855d
Create Date: 2012-10-17 16:11:50.718458

"""

# revision identifiers, used by Alembic.
revision = '2878cafe175e'
down_revision = '38c552ae855d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('ShippingAddress_ibfk_6', 'ShippingAddress', ['first_name'])
    op.create_index('ShippingAddress_ibfk_7', 'ShippingAddress', ['last_name'])
    op.create_index('ShippingAddress_ibfk_8', 'ShippingAddress', ['first_name_kana'])
    op.create_index('ShippingAddress_ibfk_9', 'ShippingAddress', ['last_name_kana'])

def downgrade():
    op.drop_index('ShippingAddress_ibfk_6', 'ShippingAddress')
    op.drop_index('ShippingAddress_ibfk_7', 'ShippingAddress')
    op.drop_index('ShippingAddress_ibfk_8', 'ShippingAddress')
    op.drop_index('ShippingAddress_ibfk_9', 'ShippingAddress')
