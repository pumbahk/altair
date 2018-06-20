"""add_column_organizationsetting_enable_price_batch_update

Revision ID: 2fecb351192b
Revises: 34ed7cee0c78
Create Date: 2018-06-20 09:49:41.857835

"""

# revision identifiers, used by Alembic.
revision = '2fecb351192b'
down_revision = '34ed7cee0c78'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_price_batch_update', sa.Boolean(), nullable=False, default=False))


def downgrade():
    op.drop_column('OrganizationSetting', 'enable_price_batch_update')
