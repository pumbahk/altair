"""Add enbale_skidata to OrganizationSetting.

Revision ID: 237be36dd727
Revises: 84ef9b4c08e
Create Date: 2019-10-07 14:01:13.085092

"""

# revision identifiers, used by Alembic.
revision = '237be36dd727'
down_revision = '84ef9b4c08e'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('enable_skidata', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('OrganizationSetting', 'enable_skidata')
