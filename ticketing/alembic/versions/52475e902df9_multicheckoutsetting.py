"""MulticheckoutSetting -> OrganizationSetting

Revision ID: 52475e902df9
Revises: 4c5e26d964ca
Create Date: 2013-03-27 16:55:01.307610

"""

# revision identifiers, used by Alembic.
revision = '52475e902df9'
down_revision = '4c5e26d964ca'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('multicheckout_shop_name', sa.Unicode(255), unique=True))
                  
    op.add_column('OrganizationSetting',
                  sa.Column('multicheckout_shop_id', sa.Unicode(255)))
                  
    op.add_column('OrganizationSetting',
                  sa.Column('multicheckout_auth_id', sa.Unicode(255)))
                  
    op.add_column('OrganizationSetting',
                  sa.Column('multicheckout_auth_password', sa.Unicode(255)))
                  

def downgrade():
    op.drop_column('OrganizationSetting', 'multicheckout_shop_name')
    op.drop_column('OrganizationSetting', 'multicheckout_shop_id')
    op.drop_column('OrganizationSetting', 'multicheckout_auth_id')
    op.drop_column('OrganizationSetting', 'multicheckout_auth_password')
