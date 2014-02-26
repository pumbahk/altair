"""add column ReportSetting.report_type

Revision ID: 4d55e04a04b2
Revises: 57e67855787e
Create Date: 2014-02-24 11:49:07.412225

"""

# revision identifiers, used by Alembic.
revision = '4d55e04a04b2'
down_revision = '57e67855787e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'ReportSetting', sa.Column(u'report_type', sa.Integer, nullable=False, default=1, server_default='1'))

def downgrade():
    op.drop_column(u'ReportSetting', u'report_type')
