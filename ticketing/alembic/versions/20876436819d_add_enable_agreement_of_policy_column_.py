"""Add enable_agreement_of_policy column to OrganizationSetting

Revision ID: 20876436819d
Revises: 573acbd34f51
Create Date: 2018-11-02 15:12:38.315911

"""

# revision identifiers, used by Alembic.
revision = '20876436819d'
down_revision = '573acbd34f51'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_agreement_of_policy', sa.Boolean(), nullable=False, server_default='0'))


def downgrade():
    op.drop_column('OrganizationSetting', 'enable_agreement_of_policy')
