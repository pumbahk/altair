"""create_discount_code_target_stock_type

Revision ID: 2e01f7df1fb8
Revises: 315fe12bd8d2
Create Date: 2018-12-18 16:03:22.387412

"""

# revision identifiers, used by Alembic.
revision = '2e01f7df1fb8'
down_revision = '315fe12bd8d2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'DiscountCodeTargetStockType',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_setting_id', Identifier, nullable=False),
        sa.Column('event_id', Identifier, nullable=True),
        sa.Column('performance_id', Identifier, nullable=True),
        sa.Column('stock_type_id', Identifier, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_setting_id'], ['DiscountCodeSetting.id'],
                                name="DiscountCodeTargetStockType_ibfk_1"),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], name="DiscountCodeTargetStockType_ibfk_2"),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="DiscountCodeTargetStockType_ibfk_3"),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], name="DiscountCodeTargetStockType_ibfk_4"),
        sa.UniqueConstraint('discount_code_setting_id', 'event_id', 'performance_id', 'stock_type_id', 'deleted_at',
                            name='unique_target_stock_type'),
    )


def downgrade():
    op.drop_table('DiscountCodeTargetStockType')
