"""add augus settings in OrganizationSetting

Revision ID: 4787aa38d83b
Revises: 2eb55c0f52e
Create Date: 2014-02-19 21:11:38.342982

"""

# revision identifiers, used by Alembic.
revision = '4787aa38d83b'
down_revision = '2eb55c0f52e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('OrganizationSetting', sa.Column('augus_use', sa.Boolean(), nullable=True, default=False))
    op.add_column('OrganizationSetting', sa.Column('augus_upload_url', sa.Unicode(length=255), nullable=True, default=u''))
    op.add_column('OrganizationSetting', sa.Column('augus_download_url', sa.Unicode(length=255), nullable=True, default=u''))
    op.add_column('OrganizationSetting', sa.Column('augus_username', sa.Unicode(length=255), nullable=True, default=u''))
    op.add_column('OrganizationSetting', sa.Column('augus_password', sa.Unicode(length=255), nullable=True, default=u''))

def downgrade():
    op.drop_column('OrganizationSetting', 'augus_use')
    op.drop_column('OrganizationSetting', 'augus_upload_url')
    op.drop_column('OrganizationSetting', 'augus_download_url')
    op.drop_column('OrganizationSetting', 'augus_username')
    op.drop_column('OrganizationSetting', 'augus_password')
