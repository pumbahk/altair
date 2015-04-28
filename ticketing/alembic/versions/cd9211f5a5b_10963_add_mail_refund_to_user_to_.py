"""#10963 add mail_refund_to_user to OrganizationSetting

Revision ID: cd9211f5a5b
Revises: 34fa171a4ba0
Create Date: 2015-04-27 18:17:41.042520

"""

# revision identifiers, used by Alembic.
revision = 'cd9211f5a5b'
down_revision = '34fa171a4ba0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('mail_refund_to_user', sa.Boolean(), nullable=False, default=False, server_default='0'))

def downgrade():
    op.drop_column('OrganizationSetting', 'mail_refund_to_user')
