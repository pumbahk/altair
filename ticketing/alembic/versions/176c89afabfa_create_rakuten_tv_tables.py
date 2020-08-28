"""create rakuten tv tables

Revision ID: 176c89afabfa
Revises: 400b8d1e91cd
Create Date: 2020-08-28 10:10:24.270840

"""

# revision identifiers, used by Alembic.
revision = '176c89afabfa'
down_revision = '400b8d1e91cd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('RakutenTvSetting',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('performance_id', Identifier(), nullable=False),
                    sa.Column('available_flg', sa.Boolean(), nullable=False, default=False, server_default=text('0')),
                    sa.Column('rtv_endpoint_url', sa.Unicode(length=512), nullable=True),
                    sa.Column('description', sa.TEXT(), nullable=True, default=""),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'RakutenTvSetting_ibfk_1'),
                    sa.PrimaryKeyConstraint('id'),
                    )

    op.create_table('RakutenTvSalesData',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('rakuten_tv_setting_id', Identifier(), nullable=False),
                    sa.Column('order_no', sa.Unicode(length=255), index=True, nullable=False),
                    sa.Column('easy_id', sa.Unicode(length=16), index=True, nullable=False),
                    sa.Column('paid_at', sa.DateTime, nullable=True),
                    sa.Column('canceled_at', sa.DateTime, nullable=True),
                    sa.Column('refunded_at', sa.DateTime, nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['rakuten_tv_setting_id'], ['RakutenTvSetting.id'], 'RakutenTvSalesData_ibfk_1'),
                    sa.PrimaryKeyConstraint('id'),
                    )

def downgrade():
    op.drop_constraint('RakutenTvSalesData_ibfk_1', 'RakutenTvSalesData', 'foreignkey')
    op.drop_table('RakutenTvSalesData')

    op.drop_constraint('RakutenTvSetting_ibfk_1', 'RakutenTvSetting', 'foreignkey')
    op.drop_table('RakutenTvSetting')
