"""alter table ReportSetting add column recipients

Revision ID: 2b30dad51162
Revises: 3ffc0a24682c
Create Date: 2013-04-15 10:12:13.568585

"""

# revision identifiers, used by Alembic.
revision = '2b30dad51162'
down_revision = '3ffc0a24682c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'ReportSetting', sa.Column('day_of_week', sa.Integer, nullable=True, default=None))
    op.add_column(u'ReportSetting', sa.Column('time', sa.String(4), nullable=True, default=None))
    op.add_column(u'ReportSetting', sa.Column('start_on', sa.DateTime(), nullable=True, default=None))
    op.add_column(u'ReportSetting', sa.Column('end_on', sa.DateTime(), nullable=True, default=None))

def downgrade():
    op.drop_column(u'ReportSetting', 'day_of_week')
    op.drop_column(u'ReportSetting', 'time')
    op.drop_column(u'ReportSetting', 'start_on')
    op.drop_column(u'ReportSetting', 'end_on')
