"""create_sales_segment_setting_and_sales_segment_group_setting

Revision ID: b58b20bfeae
Revises: 47f9f36603d6
Create Date: 2014-01-27 13:17:12.524570

"""

# revision identifiers, used by Alembic.
revision = 'b58b20bfeae'
down_revision = '47f9f36603d6'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SalesSegmentGroupSetting',
        sa.Column("id", Identifier(), autoincrement=True, nullable=False),
        sa.Column("sales_segment_group_id", Identifier(), nullable=False),
        sa.Column("order_limit", sa.Integer(), nullable=True, default=text('NULL')),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sales_segment_group_id"], ["SalesSegmentGroup.id"], "SalesSegmentGroupSetting_ibfk_1", ondelete='cascade')
        )
    op.create_table('SalesSegmentSetting',
        sa.Column("id", Identifier(), autoincrement=True, nullable=False),
        sa.Column("sales_segment_id", Identifier(), nullable=False),
        sa.Column("order_limit", sa.Integer(), nullable=True, default=text('NULL')),
        sa.Column("use_default_order_limit", sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["sales_segment_id"], ["SalesSegment.id"], "SalesSegmentSetting_ibfk_1", ondelete='cascade')
        )
    op.add_column('PerformanceSetting', sa.Column("order_limit", sa.Integer(), nullable=True, default=text('NULL')))
    op.add_column('EventSetting', sa.Column("order_limit", sa.Integer(), nullable=True, default=text('NULL')))
    op.execute("INSERT INTO SalesSegmentGroupSetting (sales_segment_group_id, order_limit) SELECT id, order_limit FROM SalesSegmentGroup")
    op.execute("INSERT INTO SalesSegmentSetting (sales_segment_id, order_limit, use_default_order_limit) SELECT id, order_limit, use_default_order_limit FROM SalesSegment")

def downgrade():
    op.drop_table("SalesSegmentGroupSetting")
    op.drop_table("SalesSegmentSetting")
    op.drop_column('PerformanceSetting', 'order_limit')
    op.drop_column('EventSetting', 'order_limit')
    # op.drop_column("SalesSegmentGroup", "order_limit")
    # op.drop_column("SalesSegment", "order_limit")
