"""create table ReportRecipient

Revision ID: 1f58bbaedf02
Revises: 2c46064b0c0a
Create Date: 2014-07-15 11:52:30.834581

"""

# revision identifiers, used by Alembic.
revision = '1f58bbaedf02'
down_revision = 'a93891ae861'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ReportRecipient',
        sa.Column('id', Identifier(), primary_key=True),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'ReportRecipient_ibfk_1', ondelete='cascade'),
        )
    op.create_table('ReportSetting_ReportRecipient',
        sa.Column('report_setting_id', Identifier(), nullable=False),
        sa.Column('report_recipient_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('report_setting_id', 'report_recipient_id'),
        sa.ForeignKeyConstraint(['report_setting_id'], ['ReportSetting.id'], 'ReportSetting_ReportRecipient_ibfk_1', ondelete='cascade'),
        sa.ForeignKeyConstraint(['report_recipient_id'], ['ReportRecipient.id'], 'ReportSetting_ReportRecipient_ibfk_2', ondelete='cascade')
        )

def downgrade():
    op.drop_constraint('ReportSetting_ReportRecipient_ibfk_2', 'ReportSetting_ReportRecipient', type_='foreignkey')
    op.drop_constraint('ReportSetting_ReportRecipient_ibfk_1', 'ReportSetting_ReportRecipient', type_='foreignkey')
    op.drop_table('ReportSetting_ReportRecipient')
    op.drop_constraint('ReportRecipient_ibfk_1', 'ReportRecipient', type_='foreignkey')
    op.drop_table('ReportRecipient')
