"""fix_too_long_keys

Revision ID: 148ac8e356cc
Revises: 185c98fe4e30
Create Date: 2013-07-24 13:39:19.262288

"""

# revision identifiers, used by Alembic.
revision = '148ac8e356cc'
down_revision = '185c98fe4e30'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def alter_index(name, tablename, columns, **kwargs):
    op.drop_index(name, tablename)
    op.create_index(name, tablename, columns, **kwargs)

INDEXES = [
    (['apikey', 'APIKey', ['apikey']], 40),
    (['host_name_path', 'Host', ['host_name', 'path']], 32),
    (['shop_name', 'MulticheckoutSetting', ['shop_name']], 48),
    (['multicheckout_shop_name', 'OrganizationSetting', ['multicheckout_shop_name']], 48),
    (['ix_Permission_category_name', 'Permission', ['category_name']], 48),
    (['ShippingAddress_ibfk_6', 'ShippingAddress', ['first_name']], 32),
    (['ShippingAddress_ibfk_7', 'ShippingAddress', ['last_name']], 32),
    (['ShippingAddress_ibfk_8', 'ShippingAddress', ['first_name_kana']], 32),
    (['ShippingAddress_ibfk_9', 'ShippingAddress', ['last_name_kana']], 32),
    ]


def upgrade():
    for args, length in INDEXES:
        alter_index(*args, mysql_length=length)

def downgrade():
    for args, _ in INDEXES:
        alter_index(*args)
