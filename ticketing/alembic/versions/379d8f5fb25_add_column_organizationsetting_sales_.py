"""add_column OrganizationSetting.sales_report_type

Revision ID: 379d8f5fb25
Revises: 3f01910d65e7
Create Date: 2014-05-23 15:44:41.312152

"""

# revision identifiers, used by Alembic.
revision = '379d8f5fb25'
down_revision = '3f01910d65e7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'OrganizationSetting', sa.Column(u'sales_report_type', sa.Integer, nullable=False, default=1, server_default='1'))

def downgrade():
    op.drop_column(u'OrganizationSetting', u'sales_report_type')
