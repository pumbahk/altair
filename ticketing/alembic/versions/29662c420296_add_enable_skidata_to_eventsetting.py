"""Add enable_skidata to EventSetting.

Revision ID: 29662c420296
Revises: 2c18d9d4fa27
Create Date: 2019-10-23 10:56:53.033068

"""

# revision identifiers, used by Alembic.
revision = '29662c420296'
down_revision = '2c18d9d4fa27'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.add_column('EventSetting', sa.Column('enable_skidata', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('EventSetting', 'enable_skidata')
