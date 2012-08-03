"""drop_stock_type_id_from_seat

Revision ID: 35b86939aab4
Revises: 7fd74bf0044
Create Date: 2012-07-30 11:39:23.239091

"""

# revision identifiers, used by Alembic.
revision = '35b86939aab4'
down_revision = '7fd74bf0044'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger

def upgrade():
    op.drop_constraint('Seat_ibfk_2', 'Seat', 'foreignkey')
    op.drop_column('Seat', 'stock_type_id') 

def downgrade():
    op.add_column('Seat', sa.Column('stock_type_id', Identifier, nullable=True))
    op.create_foreign_key('Seat_ibfk_2', 'Seat', 'StockType', ['stock_type_id'], ['id'])
