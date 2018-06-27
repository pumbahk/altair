"""create_tables_for_price_batch_update

Revision ID: 414f5d7e22cc
Revises: 2fecb351192b
Create Date: 2018-06-20 10:02:46.723050

"""

# revision identifiers, used by Alembic.
revision = '414f5d7e22cc'
down_revision = '2fecb351192b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'PriceBatchUpdateTask',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('organization_id', Identifier, nullable=False, index=True),
        sa.Column('performance_id', Identifier, nullable=False, index=True),
        sa.Column('operator_id', Identifier, nullable=False, index=True),
        sa.Column('status', sa.Integer(), nullable=False),
        sa.Column('count_updated', sa.Integer(), nullable=True, default=None),
        sa.Column('error', sa.String(20), nullable=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'],
                                'PriceBatchUpdateTask_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'],
                                'PriceBatchUpdateTask_ibfk_2', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'],
                                'PriceBatchUpdateTask_ibfk_3', ondelete='CASCADE')
    )
    op.create_table(
        'PriceBatchUpdateEntry',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('price_batch_update_task_id', Identifier, nullable=False, index=True),
        sa.Column('sales_segment_id', Identifier, nullable=False, index=True),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('price', sa.Numeric(precision=16, scale=2), nullable=False),
        sa.Column('error', sa.String(20), nullable=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['price_batch_update_task_id'], ['PriceBatchUpdateTask.id'],
                                'PriceBatchUpdateEntry_ibfk_1', ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sales_segment_id'], ['SalesSegment.id'],
                                'PriceBatchUpdateEntry_ibfk_2', ondelete='CASCADE')
    )


def downgrade():
    op.drop_table('PriceBatchUpdateEntry')
    op.drop_table('PriceBatchUpdateTask')
