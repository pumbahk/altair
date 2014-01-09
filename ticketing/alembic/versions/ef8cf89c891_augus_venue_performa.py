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
    tables = ['AugusVenue',
              'AugusSeat',
              'AugusPerformance',
              'AugusTicket',
              'AugusStockInfo',
              'AugusPutback',
              ]
    for table in tables:
        try:
            op.drop_table(table)
        except:
            pass

    op.create_table(
        'AugusVenue',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('code', sa.Integer, nullable=False),
        sa.Column('name', sa.Unicode(32), nullable=False),
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
        sa.Column('id', Identifier, primary_key=True),        
        sa.Column('area_name', sa.Unicode(32), nullable=False, default=u''),
        sa.Column('info_name', sa.Unicode(32), nullable=False, default=u''),
        sa.Column('doorway_name', sa.Unicode(32), nullable=False, default=u''),
        sa.Column('priority', sa.Integer, nullable=False, default=u''),
        sa.Column('floor', sa.Unicode(32), nullable=False),
        sa.Column('column', sa.Unicode(32), nullable=False),
        sa.Column('number', sa.Unicode(32), nullable=False),
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
        sa.Column('augus_venue_id', Identifier, nullable=False),
        sa.Column('seat_id', Identifier, nullable=False),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusPerformance',
        sa.Column('id', Identifier, primary_key=True),        
        sa.Column('augus_event_code', sa.Integer, nullable=False),        
        sa.Column('augus_performance_code', sa.Integer, nullable=False),        
        sa.Column('augus_venue_code', sa.Integer, nullable=False),
        sa.Column('augus_venue_name', sa.Unicode(32), nullable=False),
        sa.Column('augus_event_name', sa.Unicode(32), nullable=False),
        sa.Column('augus_performance_name', sa.Unicode(32), nullable=False),
        sa.Column('open_on', sa.TIMESTAMP(), nullable=True),
        sa.Column('augus_venue_version', sa.Integer, nullable=False),
        sa.Column('start_on', sa.TIMESTAMP(), nullable=True),
        # links
        sa.Column('performance_id', Identifier, nullable=False, unique=True),        
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusTicket',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('augus_event_code', sa.Integer, nullable=False),
        sa.Column('augus_performance_code', sa.Integer, nullable=False),
        sa.Column('augus_venue_code', sa.Integer, nullable=False),
        sa.Column('augus_seat_type_code', sa.Integer, nullable=False),
        sa.Column('augus_seat_type_name', sa.Unicode(32), nullable=False),
        sa.Column('unit_value_name', sa.Unicode(32), nullable=False),
        sa.Column('augus_seat_type_classif', sa.Unicode(32), nullable=False),
        sa.Column('value', sa.Integer, nullable=False),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusStockInfo',
        sa.Column('id', Identifier, primary_key=True),        
        sa.Column('augus_performance_id', Identifier, nullable=False),
        sa.Column('augus_distribution_code', sa.Integer),
        sa.Column('seat_type_classif', sa.Unicode(32)),
        sa.Column('distributed_at', sa.TIMESTAMP(), nullable=True),
        # links
        sa.Column('stock_id', Identifier, nullable=False),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(), server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    op.create_table(
        'AugusPutback',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('augus_putback_code', sa.Integer, nullable=False),                
        sa.Column('quantity', sa.Integer, nullable=False),
        sa.Column('augus_stock_info_id', Identifier, nullable=False),
        sa.Column('finished_at', sa.TIMESTAMP(), nullable=True),
        )
    op.add_column(
        'StockHolder',
        sa.Column('putback_target', sa.Integer, nullable=True),
        )

def downgrade():
    tables = ['AugusVenue',
              'AugusSeat',
              'AugusPerformance',
              'AugusTicket',
              'AugusStockInfo',
              'AugusPutback',
              ]
    for table in tables:
        op.drop_table(table)
    op.drop_column('StockHolder', 'putback_target')

        
