"""alter ReportSetting table add column last_sent_at

Revision ID: 8d3e9ae2ecf
Revises: 31d1cabf1a08
Create Date: 2016-11-14 16:51:22.715801

"""

# revision identifiers, used by Alembic.
revision = '8d3e9ae2ecf'
down_revision = '31d1cabf1a08'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'ReportSetting', sa.Column('last_sent_at', sa.TIMESTAMP(), nullable=True))

def downgrade():
    op.drop_column('ReportSetting', 'last_sent_at')
