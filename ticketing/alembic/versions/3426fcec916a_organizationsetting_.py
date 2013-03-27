"""OrganizationSetting.cart_item_name

Revision ID: 3426fcec916a
Revises: 2d8a61d70c3f
Create Date: 2013-03-27 18:01:10.973895

"""

# revision identifiers, used by Alembic.
revision = '3426fcec916a'
down_revision = '2d8a61d70c3f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('cart_item_name', sa.Unicode(255)))

def downgrade():
    op.drop_column('OrganizationSetting', 'cart_item_name')
