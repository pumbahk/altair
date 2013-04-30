"""alter table ReportSetting add column performance_id

Revision ID: 5ba25a31748
Revises: d0baadd71cc
Create Date: 2013-04-26 17:33:11.134106

"""

# revision identifiers, used by Alembic.
revision = '5ba25a31748'
down_revision = 'd0baadd71cc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('ReportSetting', 'event_id', nullable=True, name='event_id', existing_type=Identifier, existing_nullable=False)
    op.add_column(u'ReportSetting', sa.Column('performance_id', Identifier, nullable=True))
    op.execute('UPDATE ReportSetting SET operator_id = NULL WHERE operator_id = 0')
    op.drop_constraint(u'ReportSetting_ibfk_1', u'ReportSetting', type="foreignkey")
    op.create_index('ix_ReportSetting_performance_id', 'ReportSetting', ['performance_id'])

def downgrade():
    op.drop_index('ix_ReportSetting_performance_id', 'ReportSetting')
    op.create_foreign_key(u'ReportSetting_ibfk_1', 'ReportSetting', 'Event', ['event_id'], ['id'], ondelete='CASCADE')
    op.execute('UPDATE ReportSetting SET operator_id = 0 WHERE operator_id IS NULL')
    op.drop_column(u'ReportSetting', 'performance_id')
    op.alter_column('ReportSetting', 'event_id', nullable=False, name='event_id', existing_type=Identifier, existing_nullable=True)
