"""add_default_mail_sender_to_organization_setting

Revision ID: 461b4010631c
Revises: 2b70bbe205d5
Create Date: 2014-04-01 11:22:48.239819

"""

# revision identifiers, used by Alembic.
revision = '461b4010631c'
down_revision = '2b70bbe205d5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('default_mail_sender', sa.Unicode(128), nullable=False, server_default=u''))
    op.execute('UPDATE OrganizationSetting JOIN Organization ON OrganizationSetting.organization_id=Organization.id SET OrganizationSetting.default_mail_sender=Organization.contact_email')

def downgrade():
    op.drop_column('OrganizationSetting', 'default_mail_sender')
