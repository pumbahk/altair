"""change rakuten tv sales data table

Revision ID: 31d5849ba1d3
Revises: 176c89afabfa
Create Date: 2020-09-09 19:05:49.434260

"""

# revision identifiers, used by Alembic.
revision = '31d5849ba1d3'
down_revision = '176c89afabfa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('RakutenTvSalesData', sa.Column('performance_id', Identifier(), nullable=False, index=True))
    op.drop_constraint('RakutenTvSalesData_ibfk_1', 'RakutenTvSalesData', 'foreignkey')
    op.create_index('ix_RakutenTvSalesData_rakuten_tv_setting_id', 'RakutenTvSalesData', ['rakuten_tv_setting_id'])
    op.create_index('ix_RakutenTvSalesData_performance_id', 'RakutenTvSalesData', ['performance_id'])

    op.drop_constraint('RakutenTvSetting_ibfk_1', 'RakutenTvSetting', 'foreignkey')
    op.create_index('ix_RakutenTvSetting_performance_id', 'RakutenTvSetting', ['performance_id'])
    op.add_column('RakutenTvSetting', sa.Column('release_date', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('RakutenTvSetting', 'release_date')
    op.drop_index('ix_RakutenTvSetting_performance_id', 'RakutenTvSetting')
    op.create_foreign_key('RakutenTvSetting_ibfk_1', 'RakutenTvSetting', 'Performance', ['performance_id'], ['id'])

    op.drop_index('ix_RakutenTvSalesData_performance_id', 'RakutenTvSalesData')
    op.drop_index('ix_RakutenTvSalesData_rakuten_tv_setting_id', 'RakutenTvSalesData')
    op.create_foreign_key('RakutenTvSalesData_ibfk_1', 'RakutenTvSalesData', 'RakutenTvSetting', ['rakuten_tv_setting_id'], ['id'])
    op.drop_column('RakutenTvSalesData', 'performance_id')