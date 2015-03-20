"""add_auth_type_to_cart_setting

Revision ID: 34fa171a4ba0
Revises: 3c5148141687
Create Date: 2015-04-10 14:11:46.160850

"""

# revision identifiers, used by Alembic.
revision = '34fa171a4ba0'
down_revision = '3c5148141687'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('CartSetting', sa.Column('auth_type', sa.Unicode(255)))
    op.add_column('CartSetting', sa.Column('secondary_auth_type', sa.Unicode(255)))
    op.execute('UPDATE CartSetting JOIN OrganizationSetting ON CartSetting.organization_id=OrganizationSetting.organization_id SET CartSetting.auth_type=OrganizationSetting.auth_type')

def downgrade():
    op.drop_column('CartSetting', 'auth_type')
    op.drop_column('CartSetting', 'secondary_auth_type')
