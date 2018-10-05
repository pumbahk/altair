"""Add enable_point_allocation column to OrganizationSetting

Revision ID: 367c56cd18b3
Revises: 3ca4e33768b4
Create Date: 2018-10-05 13:59:16.314376

"""

# revision identifiers, used by Alembic.
revision = '367c56cd18b3'
down_revision = '3ca4e33768b4'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_point_allocation', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('OrganizationSetting', 'enable_point_allocation')
