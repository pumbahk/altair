# -*- coding: utf-8 -*-
"""add defaut_oauth_setting column to OrganizationSetting

Revision ID: 3b52df7b7879
Revises: 8d3e9ae2ecf
Create Date: 2016-11-17 10:07:21.893349

"""

# revision identifiers, used by Alembic.
revision = '3b52df7b7879'
down_revision = '8d3e9ae2ecf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import JSONEncodedDict

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('default_oauth_setting', JSONEncodedDict(8192), nullable=False, default={}, server_default='{}'),)
    # init column
    op.execute("""UPDATE OrganizationSetting SET default_oauth_setting='{"oauth_client_id": "", "oauth_client_secret": "", "oauth_endpoint_authz": "", "oauth_endpoint_api": "", "oauth_endpoint_token": "", "oauth_endpoint_token_revocation": "", "oauth_scope": "", "openid_prompt": "", "oauth_service_provider": ""}'; """)

def downgrade():
    op.drop_column('OrganizationSetting', 'default_oauth_setting')
