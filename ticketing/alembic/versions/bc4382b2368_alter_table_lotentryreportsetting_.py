"""alter table LotEntryReportSetting modify column time

Revision ID: bc4382b2368
Revises: 520345d0d89f
Create Date: 2014-05-09 10:50:37.591704

"""

# revision identifiers, used by Alembic.
revision = 'bc4382b2368'
down_revision = '520345d0d89f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('LotEntryReportSetting', 'time', nullable=True, existing_nullable=False, existing_type=sa.String(4))
    op.execute('UPDATE LotEntryReportSetting SET time = CONCAT(LPAD(time, 2, "0"), "10")')

def downgrade():
    op.execute('UPDATE LotEntryReportSetting SET time = TRIM("0" FROM SUBSTR(time, 1, 2))')
    op.alter_column('LotEntryReportSetting', 'time', nullable=False, existing_nullable=True, existing_type=sa.String(4))
