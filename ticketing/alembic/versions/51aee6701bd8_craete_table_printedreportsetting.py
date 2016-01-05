"""craete table PrintedReportSetting

Revision ID: 51aee6701bd8
Revises: 38b6b43b7e5d
Create Date: 2016-01-08 15:49:41.088078

"""

# revision identifiers, used by Alembic.
revision = '51aee6701bd8'
down_revision = '38b6b43b7e5d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PrintedReportSetting',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('start_on', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('end_on', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'PrintedReportSetting_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'PrintedReportSetting_ibfk_2', ondelete='CASCADE'),
        )

    op.create_table('PrintedReportRecipient',
        sa.Column('id', Identifier(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'PrintedReportRecipient_ibfk_1', ondelete='cascade'),
        )

    op.create_table('PrintedReportSetting_PrintedReportRecipient',
        sa.Column('report_setting_id', Identifier(), nullable=False),
        sa.Column('report_recipient_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('report_setting_id', 'report_recipient_id'),
        sa.ForeignKeyConstraint(['report_setting_id'], ['PrintedReportSetting.id'], 'PrintedReportSetting_PrintedReportRecipient_ibfk_1', ondelete='cascade'),
        sa.ForeignKeyConstraint(['report_recipient_id'], ['PrintedReportRecipient.id'], 'PrintedReportSetting_PrintedReportRecipient_ibfk_2', ondelete='cascade')
        )

def downgrade():
    op.drop_constraint('PrintedReportSetting_PrintedReportRecipient_ibfk_2', 'PrintedReportSetting_PrintedReportRecipient', type_='foreignkey')
    op.drop_constraint('PrintedReportSetting_PrintedReportRecipient_ibfk_1', 'PrintedReportSetting_PrintedReportRecipient', type_='foreignkey')
    op.drop_table('PrintedReportSetting_PrintedReportRecipient')

    op.drop_constraint('PrintedReportRecipient_ibfk_1', 'PrintedReportRecipient', type_='foreignkey')
    op.drop_table('PrintedReportRecipient')

    op.drop_constraint('PrintedReportSetting_ibfk_1', 'PrintedReportSetting', type='foreignkey')
    op.drop_constraint('PrintedReportSetting_ibfk_2', 'PrintedReportSetting', type='foreignkey')
    op.drop_table('PrintedReportSetting')
