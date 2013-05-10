"""alter table ReportSetting add column period

Revision ID: 489071e335a
Revises: 5129fbc59530
Create Date: 2013-05-10 10:19:27.530583

"""

# revision identifiers, used by Alembic.
revision = '489071e335a'
down_revision = '5129fbc59530'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'ReportSetting', sa.Column('period', sa.Integer, nullable=False))
    op.execute('UPDATE ReportSetting SET period = 1')
    op.alter_column('ReportSetting', 'frequency', nullable=False, existing_nullable=True, existing_type=sa.Integer)
    op.alter_column('ReportSetting', 'time', nullable=False, existing_nullable=True, existing_type=sa.String(4))

def downgrade():
    op.alter_column('ReportSetting', 'time', nullable=True, existing_nullable=False, existing_type=sa.String(4))
    op.alter_column('ReportSetting', 'frequency', nullable=True, existing_nullable=False, existing_type=sa.Integer)
    op.drop_column(u'ReportSetting', 'period')
