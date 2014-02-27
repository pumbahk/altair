"""alter table SalesSegmentSetting alter column use_default_disp_orderreview

Revision ID: 3c93bddaec70
Revises: 4d55e04a04b2
Create Date: 2014-02-27 15:59:07.428150

"""

# revision identifiers, used by Alembic.
revision = '3c93bddaec70'
down_revision = '4d55e04a04b2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('SalesSegmentSetting', 'use_default_disp_orderreview')
    op.add_column('SalesSegmentSetting', sa.Column('use_default_disp_orderreview', sa.Boolean(), nullable=True,default=True, server_default=text('1')))

def downgrade():
    op.drop_column('SalesSegmentSetting', 'use_default_disp_orderreview')
    op.add_column('SalesSegmentSetting', sa.Column('use_default_disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
