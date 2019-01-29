"""Add column OrganizationSetting enable_spa_cart

Revision ID: 16d8ed4fdf59
Revises: 2e01f7df1fb8
Create Date: 2019-01-16 21:09:44.779340

"""

# revision identifiers, used by Alembic.
revision = '16d8ed4fdf59'
down_revision = '2e01f7df1fb8'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_spa_cart', sa.Boolean(), nullable=False, server_default='0'))

def downgrade():
    op.drop_column('OrganizationSetting', 'enable_spa_cart')
