"""augus

Revision ID: a4caeb81d1b
Revises: f0a2ca58baa
Create Date: 2013-11-05 10:38:15.551115

"""

# revision identifiers, used by Alembic.
revision = 'a4caeb81d1b'
down_revision = 'f0a2ca58baa'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
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
        # extra
        sa.UniqueConstraint('area_code', 'info_code', 'floor', 'column', 'num',
                            'augus_venue_id', name='uix_AugusSeat'),
        )

def downgrade():
    op.drop_table('AugusVenue')
    op.drop_table('AugusSeat')
