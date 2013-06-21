"""point_related_changes
Revision ID: 23d59b1d8131
Revises: fea1ae388f0
Create Date: 2013-05-13 13:19:17.829254

"""

# revision identifiers, used by Alembic.
revision = '23d59b1d8131'
down_revision = 'fea1ae388f0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting', sa.Column('point_type', sa.Integer(), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('point_fixed', sa.Numeric(precision=16, scale=2), nullable=True))
    op.add_column('OrganizationSetting', sa.Column('point_rate', sa.Float(), nullable=True))

    op.create_table('PointGrantSetting',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('organization_id', Identifier(), nullable=False),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('type', sa.Integer(), nullable=False),
        sa.Column('fixed', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('rate', sa.Float(), nullable=True),
        sa.Column('start_at', sa.DateTime(), nullable=True),
        sa.Column('end_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'PointGrantSetting_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

    op.create_table('SalesSegment_PointGrantSetting',
        sa.Column('sales_segment_id', Identifier(), nullable=False),
        sa.Column('point_grant_setting_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('sales_segment_id', 'point_grant_setting_id'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'], 'SalesSegment_PointGrantSetting_ibfk_1', onupdate='cascade', ondelete='cascade'),
        sa.ForeignKeyConstraint(['point_grant_setting_id'], ['PointGrantSetting.id'], 'SalesSegment_PointGrantSetting_ibfk_2', onupdate='cascade', ondelete='cascade')
        )

    op.create_table('PointGrantSetting_Product',
        sa.Column('point_grant_setting_id', Identifier(), nullable=False),
        sa.Column('product_id', Identifier(), nullable=False),
        sa.PrimaryKeyConstraint('point_grant_setting_id', 'product_id'),
        sa.ForeignKeyConstraint(['point_grant_setting_id'], ['PointGrantSetting.id'], 'PointGrantSetting_Product_ibfk_1', onupdate='cascade', ondelete='cascade'),
        sa.ForeignKeyConstraint(['product_id'], ['Product.id'], 'PointGrantSetting_Product_ibfk_2', onupdate='cascade', ondelete='cascade')
        )

    op.create_table('PointGrantHistoryEntry',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_point_account_id', Identifier(), nullable=False),
        sa.Column('order_id', Identifier(), nullable=True),
        sa.Column('amount', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('submitted_on', sa.Date(), nullable=False),
        sa.Column('grant_status', sa.Unicode(4), nullable=True),
        sa.Column('granted_amount', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('granted_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['user_point_account_id'], ['UserPointAccount.id'], 'PointGrantHistoryEntry_ibfk_1', ondelete='cascade'),
        sa.ForeignKeyConstraint(['order_id'], ['Order.id'], 'PointGrantHistoryEntry_ibfk_2', ondelete='cascade'),
        sa.PrimaryKeyConstraint('id')
        )
    op.drop_table('UserPointHistory')

def downgrade():
    op.create_table('UserPointHistory',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('user_point_account_id', Identifier(), nullable=True),
        sa.Column('user_id', Identifier(), nullable=True),
        sa.Column('point', sa.Integer(), nullable=True),
        sa.Column('rate', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['User.id'], 'UserPointHistory_ibfk_1', ondelete='cascade'),
        sa.ForeignKeyConstraint(['user_point_account_id'], ['UserPointAccount.id'], 'UserPointHistory_ibfk_2', ondelete='cascade'),
        sa.PrimaryKeyConstraint('id')
        )
    op.drop_table('PointGrantHistoryEntry')
    op.drop_table('PointGrantSetting_Product')
    op.drop_table('SalesSegment_PointGrantSetting')
    op.drop_table('PointGrantSetting')
    op.drop_column('OrganizationSetting', 'point_type')
    op.drop_column('OrganizationSetting', 'point_fixed')
    op.drop_column('OrganizationSetting', 'point_rate')

