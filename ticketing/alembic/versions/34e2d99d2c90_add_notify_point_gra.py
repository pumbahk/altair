"""add_notify_point_grainting_failure_to_organization_setting

Revision ID: 34e2d99d2c90
Revises: 1748d0eee30b
Create Date: 2013-11-12 20:27:34.333856

"""

# revision identifiers, used by Alembic.
revision = '34e2d99d2c90'
down_revision = '1748d0eee30b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('notify_point_granting_failure', sa.Boolean(), nullable=False, default=False))

def downgrade():
    op.drop_column('OrganizationSetting', 'notify_point_granting_failure')
