"""alter table ReportSetting add column name, email

Revision ID: e61547b1288
Revises: 2b30dad51162
Create Date: 2013-04-15 16:28:55.783836

"""

# revision identifiers, used by Alembic.
revision = 'e61547b1288'
down_revision = '2b30dad51162'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(u'ReportSetting', sa.Column('name', sa.String(255), nullable=True))
    op.add_column(u'ReportSetting', sa.Column('email', sa.String(255), nullable=True))
    op.drop_constraint(u'ReportSetting_ibfk_2', u'ReportSetting', type="foreignkey")
    op.alter_column('ReportSetting', 'operator_id', nullable=True, name='operator_id', existing_type=Identifier, existing_nullable=False)

def downgrade():
    op.alter_column('ReportSetting', 'operator_id', nullable=False, name='operator_id', existing_type=Identifier, existing_nullable=True)
    op.create_foreign_key(u'ReportSetting_ibfk_2', 'ReportSetting', 'Operator', ['operator_id'], ['id'])
    op.drop_column(u'ReportSetting', 'email')
    op.drop_column(u'ReportSetting', 'name')
