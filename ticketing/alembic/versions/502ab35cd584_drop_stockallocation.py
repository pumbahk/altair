"""drop StockAllocation table

Revision ID: 502ab35cd584
Revises: 262ced946541
Create Date: 2012-07-25 21:32:04.567299

"""

# revision identifiers, used by Alembic.
revision = '502ab35cd584'
down_revision = '262ced946541'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.drop_table('StockAllocation')

def downgrade():
    op.create_table('StockAllocation',
        sa.Column('stock_type_id', Identifier(), nullable=False),
        sa.Column('performance_id', Identifier(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'stockallocation_ibfk_1'),
        sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], 'stockallocation_ibfk_2'),
        sa.PrimaryKeyConstraint('stock_type_id', 'performance_id')
        )
