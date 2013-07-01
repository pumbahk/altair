"""add_bcc_address_to_organization_setting

Revision ID: 20ed005e38e
Revises: 3924078740d2
Create Date: 2013-07-01 11:40:46.501211

"""

# revision identifiers, used by Alembic.
revision = '20ed005e38e'
down_revision = '3924078740d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('bcc_recipient', sa.Unicode(255), nullable=True, default=None))
    op.execute('UPDATE OrganizationSetting JOIN Organization ON OrganizationSetting.organization_id=Organization.id SET OrganizationSetting.bcc_recipient=Organization.contact_email')

def downgrade():
    op.drop_column('OrganizationSetting', 'bcc_recipient')
