"""drop column ReportSetting.email,name

Revision ID: 470ecc52bc32
Revises: 20b4a3d70ef4
Create Date: 2014-07-17 18:15:46.334444

"""

# revision identifiers, used by Alembic.
revision = '470ecc52bc32'
down_revision = '20b4a3d70ef4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('ReportSetting', 'operator_id')
    op.drop_column('ReportSetting', 'name')
    op.drop_column('ReportSetting', 'email')
    op.drop_constraint('LotEntryReportSetting_ibfk_3', 'LotEntryReportSetting', type_='foreignkey')
    op.drop_column('LotEntryReportSetting', 'operator_id')
    op.drop_column('LotEntryReportSetting', 'name')
    op.drop_column('LotEntryReportSetting', 'email')

def downgrade():
    op.add_column('LotEntryReportSetting', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('LotEntryReportSetting', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('LotEntryReportSetting', sa.Column('operator_id', Identifier, nullable=True))
    op.create_foreign_key('LotEntryReportSetting_ibfk_3', 'LotEntryReportSetting', 'Operator', ['operator_id'], ['id'], ondelete='CASCADE')
    op.add_column('ReportSetting', sa.Column('email', sa.String(255), nullable=True))
    op.add_column('ReportSetting', sa.Column('name', sa.String(255), nullable=True))
    op.add_column('ReportSetting', sa.Column('operator_id', Identifier, nullable=True))
