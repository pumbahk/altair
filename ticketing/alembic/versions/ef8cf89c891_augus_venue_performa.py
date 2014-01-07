"""augus_venue_performance

Revision ID: ef8cf89c891
Revises: 46aa7d0c688f
Create Date: 2013-12-24 17:51:40.084806

"""

# revision identifiers, used by Alembic.
revision = 'ef8cf89c891'
down_revision = '46aa7d0c688f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.create_table(
        'AugusVenue',
        sa.Column('id', Identifier, primary=True),
        sa.Column('code', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode, nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        # links
        sa.Column('venue_id', Identifier, nullable=False, unique=True),        
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusSeat',
        sa.Column('id', Identifier, primary=True),        
        sa.Column('area_name', sa.Unicode, nullable=False, default=''),
        sa.Column('info_name', sa.Unicode, nullable=False, default=''),
        sa.Column('doorway_name', sa.Unicode, nullable=False, default=''),
        sa.Column('priority', sa.Integer, nullable=False, default=''),
        sa.Column('floor', sa.Unicode, nullable=False),
        sa.Column('column', sa.Unicode, nullable=False),
        sa.Column('number', sa.Unicode, nullable=False),
        sa.Column('block', sa.Integer, nullable=False),
        sa.Column('coordy', sa.Integer, nullable=False),
        sa.Column('coordx', sa.Integer, nullable=False),
        sa.Column('coordy_whole', sa.Integer, nullable=False),
        sa.Column('coordx_whole', sa.Integer, nullable=False),
        sa.Column('area_code', sa.Integer, nullable=False),
        sa.Column('info_code', sa.Integer, nullable=False),
        sa.Column('doorway_code', sa.Integer, nullable=False),
        sa.Column('version', sa.Integer, nullable=False),
        # links
        sa.Column('seat_id', Identifier, nullable=False),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusPerformance',
        sa.Column('id', Identifier, primary=True),        
        sa.Column('augus_event_code', sa.Integer, nullable=False),        
        sa.Column('augus_performance_code', sa.Integer, nullable=False),        
        sa.Column('augus_venue_code', sa.Integer, nullable=False),
        sa.Column('augus_venue_name', sa.Unicode, nullable=False),
        sa.Column('augus_event_name', sa.Unicode, nullable=False),
        sa.Column('augus_performance_name', sa.Unicode, nullable=False),
        sa.Column('open_on', sa.TIMESTAMP(), nullable=False),
        sa.Column('start_on', sa.TIMESTAMP(), nullable=False),
        sa.Column('augus_event_version', sa.Integer, nullable=False),
        # links
        sa.Column('performance_id', Identifier, nullable=False, unique=True),        
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusTicket',
        sa.Column('id', Identifier, primary=True),
        sa.Column('augus_event_code', sa.Integer, nullable=False),
        sa.Column('augus_performance_code', sa.Integer, nullable=False),
        sa.Column('augus_venue_code', sa.Integer, nullable=False),
        sa.Column('augus_seat_type_code', sa.Integer, nullable=False),
        sa.Column('augus_seat_type_name', sa.Unicode, nullable=False),
        sa.Column('unit_value_name', sa.Unicode, nullable=False),
        sa.Column('augus_seat_type_classif', sa.Unicode, nullable=False),
        sa.Column('value', sa.Integer, nullable=False),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusStockInfo',
        sa.Column('id', Identifier, primary=True),        
        sa.Column('augus_performance_id', Identifer, nullable=False),
        sa.Column('augus_distribution_code', sa.Integer),
        sa.Column('seat_type_classif', sa.Unicode),
        sa.Column('distributed_at', sa.TIMESTAMP())
        # links
        sa.Column('stock_id'),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusPutback',
        sa.Column('id', Identifier, primary=True),
        sa.Column('augus_putback_code', sa.Integer, nullable=False),                
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('augus_stock_info_id', Identifer, nullable=False),
        sa.Column('finished_at', sa.TIMESTAMP(), nullable=True),        
        )
def downgrade():
    pass
