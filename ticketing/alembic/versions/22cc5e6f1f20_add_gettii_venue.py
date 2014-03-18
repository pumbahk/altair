"""add_gettii_venue

Revision ID: 22cc5e6f1f20
Revises: 3c93bddaec70
Create Date: 2014-03-07 13:46:46.955678

"""

# revision identifiers, used by Alembic.
revision = '22cc5e6f1f20'
down_revision = '3c93bddaec70'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'GettiiVenue',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('code', sa.Integer, nullable=False),
        # links
        sa.Column('venue_id', Identifier, nullable=False),
        )

    op.create_table(
        'GettiiSeat',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('l0_id', sa.Unicode(32), nullable=False),
        sa.Column('coordx', sa.Unicode(32), nullable=False),
        sa.Column('coordy', sa.Unicode(32), nullable=False),
        sa.Column('posx', sa.Unicode(32), nullable=False),
        sa.Column('posy', sa.Unicode(32), nullable=False),
        sa.Column('angle', sa.Unicode(32), nullable=False),
        sa.Column('floor', sa.Unicode(32), nullable=False),
        sa.Column('column', sa.Unicode(32), nullable=False),
        sa.Column('num', sa.Unicode(32), nullable=False),
        sa.Column('block', sa.Unicode(32), nullable=False),
        sa.Column('gate', sa.Unicode(32), nullable=False),
        sa.Column('priority_floor', sa.Unicode(32), nullable=False),
        sa.Column('priority_area_code', sa.Unicode(32), nullable=False),
        sa.Column('priority_block', sa.Unicode(32), nullable=False),
        sa.Column('priority_seat', sa.Unicode(32), nullable=False),
        sa.Column('seat_flag', sa.Unicode(32), nullable=False),
        sa.Column('seat_classif', sa.Unicode(32), nullable=False),
        sa.Column('net_block', sa.Unicode(32), nullable=False),
        sa.Column('modified_by', sa.Unicode(32), nullable=False),
        sa.Column('modified_at', sa.Unicode(32), nullable=False),
        # links
        sa.Column('gettii_venue_id', Identifier, nullable=False),
        sa.Column('seat_id', Identifier, nullable=False),
        )

def downgrade():
    op.drop_table('GettiiVenue')
    op.drop_table('GettiiSeat')
