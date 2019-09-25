"""Add migrate_to_sirius column to OrganizationSetting

Revision ID: 2e1dcb75573
Revises: 16d8ed4fdf59
Create Date: 2019-02-28 14:46:47.830743

"""

# revision identifiers, used by Alembic.
revision = '2e1dcb75573'
down_revision = '16d8ed4fdf59'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('migrate_to_sirius', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('OrganizationSetting', 'migrate_to_sirius')
