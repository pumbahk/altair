"""augus_product

Revision ID: 14e9e848dc88
Revises: 4787aa38d83b
Create Date: 2014-02-22 04:48:37.792170

"""

# revision identifiers, used by Alembic.
revision = '14e9e848dc88'
down_revision = '4787aa38d83b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'AugusStockDetail',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('augus_distribution_code', sa.Integer, nullable=False),
        sa.Column('augus_seat_type_code', sa.Integer, nullable=False),
        sa.Column('augus_unit_value_code', sa.Integer, nullable=False),
        sa.Column('start_on', sa.DateTime(), nullable=False),
        sa.Column('seat_tye_classif', sa.Integer, nullable=False),
        sa.Column('augus_unit_value_code', sa.Integer, nullable=False),
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('augus_stock_info_id', Identifier, nullable=False),
        sa.Column('augus_putback_id', Identifier, nullable=True),
        sa.Column('augus_ticket_id', Identifier, nullable=False),
        )
    op.add_column('AugusPutback', sa.Column('augus_stock_info_detail_id', Identifier(), nullable=True))
    op.add_column('Product', sa.Column('augus_ticket_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column('Product', 'augus_ticket_id')
    op.drop_column('AugusPutback', 'augus_stock_info_detail_id')
    op.drop_table('AugusStockDetail')
