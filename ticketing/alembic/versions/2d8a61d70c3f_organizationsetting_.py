"""OrganizationSetting.multicheckout_*

Revision ID: 2d8a61d70c3f
Revises: 52475e902df9
Create Date: 2013-03-27 17:03:27.208834

"""

# revision identifiers, used by Alembic.
revision = '2d8a61d70c3f'
down_revision = '52475e902df9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""UPDATE OrganizationSetting
JOIN MulticheckoutSetting
ON OrganizationSetting.organization_id = MulticheckoutSetting.organization_id
SET
    OrganizationSetting.multicheckout_shop_name = MulticheckoutSetting.shop_name,
    OrganizationSetting.multicheckout_shop_id = MulticheckoutSetting.shop_id,
    OrganizationSetting.multicheckout_auth_id = MulticheckoutSetting.auth_id,
    OrganizationSetting.multicheckout_auth_password = MulticheckoutSetting.auth_password

""")

def downgrade():
    pass
