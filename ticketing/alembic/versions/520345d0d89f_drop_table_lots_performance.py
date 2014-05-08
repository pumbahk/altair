"""drop table Lots_Performance

Revision ID: 520345d0d89f
Revises: f65df8d40c7
Create Date: 2014-04-28 15:20:59.674078

"""

# revision identifiers, used by Alembic.
revision = '520345d0d89f'
down_revision = 'f65df8d40c7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_table('Lots_Performance')
    op.drop_table('Lots_StockType')

def downgrade():
    op.create_table('Lots_Performance',
       sa.Column('lot_id', Identifier(), nullable=True),
       sa.Column('performance_id', Identifier(), nullable=True),
       sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="Lots_Performance_ibfk_1"),
       sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="Lots_Performance_ibfk_2"),
       sa.PrimaryKeyConstraint()
       )
    op.create_table('Lots_StockType',
       sa.Column('lot_id', Identifier(), nullable=True),
       sa.Column('stock_type_id', Identifier(), nullable=True),
       sa.ForeignKeyConstraint(['lot_id'], ['Lot.id'], name="Lots_StockType__ibfk_1"),
       sa.ForeignKeyConstraint(['stock_type_id'], ['StockType.id'], name="Lots_StockType__ibfk_2"),
       sa.PrimaryKeyConstraint()
       )
