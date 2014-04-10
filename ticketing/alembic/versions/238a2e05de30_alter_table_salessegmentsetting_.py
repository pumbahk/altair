"""alter table SalesSegmentSetting, SalesSegmentGroupSetting add column disp_agreement, agreement_body

Revision ID: 238a2e05de30
Revises: 461b4010631c
Create Date: 2014-04-08 16:54:02.773119

"""

# revision identifiers, used by Alembic.
revision = '238a2e05de30'
down_revision = '461b4010631c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'SalesSegmentGroupSetting', sa.Column(u'disp_agreement', sa.Boolean, default=False, server_default='0'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'disp_agreement', sa.Boolean, default=False, server_default='0'))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'use_default_disp_agreement', sa.Boolean(), nullable=True,default=True, server_default=text('1')))

    op.add_column(u'SalesSegmentGroupSetting', sa.Column(u'agreement_body', sa.UnicodeText()))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'agreement_body', sa.UnicodeText()))
    op.add_column(u'SalesSegmentSetting', sa.Column(u'use_default_agreement_body', sa.Boolean(), nullable=True,default=True, server_default=text('1')))

def downgrade():
    op.drop_column(u'SalesSegmentGroupSetting', u'disp_agreement')
    op.drop_column(u'SalesSegmentSetting', u'disp_agreement')
    op.drop_column(u'SalesSegmentSetting', u'use_default_disp_agreement')

    op.drop_column(u'SalesSegmentGroupSetting', u'agreement_body')
    op.drop_column(u'SalesSegmentSetting', u'agreement_body')
    op.drop_column(u'SalesSegmentSetting', u'use_default_agreement_body')
