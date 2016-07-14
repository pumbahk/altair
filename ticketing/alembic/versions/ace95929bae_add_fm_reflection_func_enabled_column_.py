"""Add fm_reflection_func_enabled column to OrganizationSetting

Revision ID: ace95929bae
Revises: 51227242a955
Create Date: 2016-07-06 19:28:30.050378

"""

# revision identifiers, used by Alembic.
revision = 'ace95929bae'
down_revision = '51227242a955'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(
        'OrganizationSetting',
        sa.Column('enable_fm_reflection_func', sa.Boolean(), nullable=False, server_default=text('TRUE'))
        )

def downgrade():
    op.drop_column('OrganizationSetting', 'enable_fm_reflection_func')
