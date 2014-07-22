"""create table LotEntryReportSetting_ReportRecipient

Revision ID: 45e17ff9f21a
Revises: 1f58bbaedf02
Create Date: 2014-07-17 16:52:02.663064

"""

# revision identifiers, used by Alembic.
revision = '45e17ff9f21a'
down_revision = '1f58bbaedf02'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('LotEntryReportSetting_ReportRecipient',
        sa.Column('lot_entry_report_setting_id', Identifier(), nullable=False),
        sa.Column('report_recipient_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('lot_entry_report_setting_id', 'report_recipient_id'),
        sa.ForeignKeyConstraint(['lot_entry_report_setting_id'], ['LotEntryReportSetting.id'], 'LotEntryReportSetting_ReportRecipient_ibfk_1', ondelete='cascade'),
        sa.ForeignKeyConstraint(['report_recipient_id'], ['ReportRecipient.id'], 'LotEntryReportSetting_ReportRecipient_ibfk_2', ondelete='cascade')
        )

def downgrade():
    op.drop_constraint('LotEntryReportSetting_ReportRecipient_ibfk_2', 'LotEntryReportSetting_ReportRecipient', type_='foreignkey')
    op.drop_constraint('LotEntryReportSetting_ReportRecipient_ibfk_1', 'LotEntryReportSetting_ReportRecipient', type_='foreignkey')
    op.drop_table('LotEntryReportSetting_ReportRecipient')
