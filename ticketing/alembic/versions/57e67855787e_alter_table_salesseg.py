"""alter table SalesSegmentGroup, SalesSegment delete column disp_orderreview and alter table SalesSegmentGroupSetting, SalesSegmentSetting add column disp_orderreview

Revision ID: 57e67855787e
Revises: 514c8ba82a38
Create Date: 2014-02-24 18:10:33.654774

"""

# revision identifiers, used by Alembic.
revision = '57e67855787e'
down_revision = '514c8ba82a38'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('SalesSegment', 'disp_orderreview')
    op.drop_column('SalesSegment', 'use_default_disp_orderreview')
    op.drop_column('SalesSegmentGroup', 'disp_orderreview')

    op.add_column('SalesSegmentSetting', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegmentSetting', sa.Column('use_default_disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegmentGroupSetting', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))


def downgrade():
    op.add_column('SalesSegment', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegment', sa.Column('use_default_disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))
    op.add_column('SalesSegmentGroup', sa.Column('disp_orderreview', sa.Boolean(), nullable=False,default=True, server_default=text('1')))

    op.drop_column('SalesSegmentSetting', 'disp_orderreview')
    op.drop_column('SalesSegmentSetting', 'use_default_disp_orderreview')
    op.drop_column('SalesSegmentGroupSetting', 'disp_orderreview')
