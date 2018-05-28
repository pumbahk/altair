"""add lots lock to OrganizationSetting

Revision ID: 4efaf35b55bf
Revises: 3cd361e34c44
Create Date: 2018-05-22 15:52:42.554896

"""

# revision identifiers, used by Alembic.
revision = '4efaf35b55bf'
down_revision = '3cd361e34c44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('lot_entry_lock', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    op.add_column('LotElectedEntry',
                  sa.Column('completed_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('OrganizationSetting', 'lot_entry_lock')
    op.drop_column('LotElectedEntry', 'completed_at')