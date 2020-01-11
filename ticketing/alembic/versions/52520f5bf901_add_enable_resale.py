"""add enable_resale SalesSegmentGroupSetting

Revision ID: 52520f5bf901
Revises: 294ca5bb74d2
Create Date: 2019-11-27 17:30:23.203595

"""

# revision identifiers, used by Alembic.
revision = '52520f5bf901'
down_revision = '294ca5bb74d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.add_column('SalesSegmentGroupSetting',
                  sa.Column('enable_resale', sa.Boolean(), nullable=False, server_default=text('0')))
    op.add_column('SalesSegmentSetting',
                  sa.Column('enable_resale', sa.Boolean(), nullable=False, server_default=text('0')))
    op.add_column('SalesSegmentSetting',
                  sa.Column('use_default_enable_resale', sa.Boolean(), nullable=False, server_default=text('1')))

def downgrade():
    op.drop_column('SalesSegmentGroupSetting', 'enable_resale')
    op.drop_column('SalesSegmentSetting', 'enable_resale')
    op.drop_column('SalesSegmentSetting', 'use_default_enable_resale')
