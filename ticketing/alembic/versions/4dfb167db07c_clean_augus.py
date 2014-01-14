"""clean_augus

Revision ID: 4dfb167db07c
Revises: 2c0aeb3996df
Create Date: 2014-01-14 16:50:29.549510

"""

# revision identifiers, used by Alembic.
revision = '4dfb167db07c'
down_revision = '2c0aeb3996df'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    tables = ['AugusVenue',
              'AugusSeat',
              'AugusPerformance',
              ]
    for table in tables:
        op.drop_table(table)

def downgrade():
    op.create_table(
        'AugusVenue',
        sa.Column('id', Identifier, nullable=False, primary_key=True),
        sa.Column('code', sa.Integer, nullable=False, unique=True),
        sa.Column('venue_id', Identifier, nullable=False, unique=True),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),        
        )
    op.create_table(
        'AugusSeat',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('area_code', sa.Integer, nullable=False),
        sa.Column('info_code', sa.Integer, nullable=False),
        sa.Column('floor', sa.Unicode(32), nullable=False),
        sa.Column('column', sa.Unicode(32), nullable=False),
        sa.Column('num', sa.Unicode(32), nullable=False),
        sa.Column('augus_venue_id', Identifier, nullable=False),
        sa.Column('seat_id', Identifier),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        )
    
    op.create_table(
        'AugusPerformance',
        sa.Column('id', Identifier, nullable=False, primary_key=True),
        sa.Column('code', sa.Integer, nullable=False, unique=True),
        sa.Column('augus_event_code', sa.Integer, nullable=False),
        sa.Column('performance_id', Identifier, nullable=True, unique=True),
        # for super class
        sa.Column('created_at', sa.TIMESTAMP(),
                  server_default=text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(),
                  server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),        
        )
