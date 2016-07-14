"""alter table PrintedReportSetting add column time and last_sent_at

Revision ID: 209707809135
Revises: ace95929bae
Create Date: 2016-07-06 15:42:43.462498

"""

# revision identifiers, used by Alembic.
revision = '209707809135'
down_revision = 'ace95929bae'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'PrintedReportSetting', sa.Column('time', sa.TIME(), nullable=True))
    op.add_column(u'PrintedReportSetting', sa.Column('last_sent_at', sa.TIMESTAMP(), nullable=True))

def downgrade():
    op.drop_column('PrintedReportSetting', 'time')
    op.drop_column('PrintedReportSetting', 'last_sent_at')
