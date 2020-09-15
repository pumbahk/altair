"""add template_status on LivePerformanceSetting

Revision ID: 46d8b483857d
Revises: 400b8d1e91cd
Create Date: 2020-09-01 11:42:21.849045

"""

# revision identifiers, used by Alembic.
revision = '46d8b483857d'
down_revision = '4c9ba136ed1d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects.mysql import TEXT

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LivePerformanceSetting',
                  sa.Column('template_type', sa.Integer(), default=1, nullable=False, server_default=text('1')))
    op.add_column('LivePerformanceSetting', sa.Column('live_chat_code', TEXT(charset='utf8'), nullable=True))
    op.add_column('LivePerformanceSetting',
                  sa.Column('public_flag', sa.Boolean, default=False, server_default=text('0')))


def downgrade():
    op.drop_column('LivePerformanceSetting', 'template_type')
    op.drop_column('LivePerformanceSetting', 'live_chat_code')
    op.drop_column('LivePerformanceSetting', 'public_flag')
