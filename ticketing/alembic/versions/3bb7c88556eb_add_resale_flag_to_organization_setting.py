"""add resale flag to organization setting

Revision ID: 3bb7c88556eb
Revises: 430e25d95def
Create Date: 2018-04-04 18:16:20.043621

"""

# revision identifiers, used by Alembic.
revision = '3bb7c88556eb'
down_revision = '430e25d95def'

from alembic import op
import sqlalchemy as sa


Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_resale', sa.Boolean, server_default='0', nullable=False))

def downgrade():
    op.drop_column('OrganizationSetting', 'enable_resale')