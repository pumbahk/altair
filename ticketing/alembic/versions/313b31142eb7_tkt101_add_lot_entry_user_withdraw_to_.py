"""tkt101 add lot_entry_user_withdraw to OrganizationSetting

Revision ID: 313b31142eb7
Revises: 6cdbdb8cd27
Create Date: 2015-11-11 16:59:51.318632

"""

# revision identifiers, used by Alembic.
revision = '313b31142eb7'
down_revision = '6cdbdb8cd27'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('lot_entry_user_withdraw', sa.Boolean(), nullable=False, default=False, server_default='0'))

def downgrade():
    op.drop_column('OrganizationSetting', 'lot_entry_user_withdraw')
