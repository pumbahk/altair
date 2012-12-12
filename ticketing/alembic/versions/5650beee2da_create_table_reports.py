"""create table ReportSetting

Revision ID: 5650beee2da
Revises: 49e6fa971a5
Create Date: 2012-11-15 12:25:05.760529

"""

# revision identifiers, used by Alembic.
revision = '5650beee2da'
down_revision = '388e34a2537a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ReportSetting',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('event_id', Identifier(), nullable=False),
        sa.Column('operator_id', Identifier(), nullable=False),
        sa.Column('frequency', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], 'ReportSetting_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], 'ReportSetting_ibfk_2', ondelete='CASCADE'),
        )

def downgrade():
    op.drop_constraint('ReportSetting_ibfk_1', 'ReportSetting', type='foreignkey')
    op.drop_constraint('ReportSetting_ibfk_2', 'ReportSetting', type='foreignkey')
    op.drop_table('ReportSetting')

