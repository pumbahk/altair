"""add_l0_seat

Revision ID: f0a2ca58baa
Revises: 34e2d99d2c90
Create Date: 2013-11-07 21:37:23.727949

"""

# revision identifiers, used by Alembic.
revision = 'f0a2ca58baa'
down_revision = '34e2d99d2c90'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'L0Seat',
        sa.Column('site_id', Identifier(), nullable=False),
        sa.Column('l0_id', sa.Unicode(48), nullable=False),
        sa.Column('row_l0_id', sa.Unicode(48), nullable=True),
        sa.Column('group_l0_id', sa.Unicode(48), nullable=True),
        sa.Column('name', sa.Unicode(50), nullable=False),
        sa.Column('seat_no', sa.Unicode(50), nullable=True),
        sa.Column('row_no', sa.Unicode(50), nullable=True),
        sa.Column('block_name', sa.Unicode(50), nullable=True),
        sa.Column('floor_name', sa.Unicode(50), nullable=True),
        sa.Column('gate_name', sa.Unicode(50), nullable=True),
        sa.PrimaryKeyConstraint('site_id', 'l0_id'),
        sa.ForeignKeyConstraint(['site_id'], ['Site.id'], name='L0Seat_ibfk_1', ondelete='cascade'),
        sa.Index('l0_id', 'l0_id')
        )
    op.execute("""
INSERT INTO L0Seat
(
    site_id,
    l0_id,
    row_l0_id,
    group_l0_id,
    name,
    seat_no,
    row_no,
    block_name,
    floor_name,
    gate_name
)
SELECT
    V.site_id,
    Seat.l0_id,
    Seat.row_l0_id,
    Seat.group_l0_id,
    Seat.name,
    Seat.seat_no,
    SeatAttribute_row.value,
    SeatAttribute_block.value,
    SeatAttribute_floor.value,
    SeatAttribute_gate.value
FROM
    (SELECT MAX(id) id, site_id FROM Venue WHERE deleted_at IS NULL GROUP BY site_id) V
    JOIN Seat
        ON Seat.venue_id=V.id
    LEFT JOIN SeatAttribute SeatAttribute_row
        ON Seat.id=SeatAttribute_row.seat_id AND SeatAttribute_row.name='row'
    LEFT JOIN SeatAttribute SeatAttribute_block
        ON Seat.id=SeatAttribute_block.seat_id AND SeatAttribute_block.name='block'
    LEFT JOIN SeatAttribute SeatAttribute_floor
        ON Seat.id=SeatAttribute_floor.seat_id AND SeatAttribute_floor.name='floor'
    LEFT JOIN SeatAttribute SeatAttribute_gate
        ON Seat.id=SeatAttribute_gate.seat_id AND SeatAttribute_gate.name='gate'
WHERE
    Seat.deleted_at IS NULL AND
    SeatAttribute_row.deleted_at IS NULL AND
    SeatAttribute_block.deleted_at IS NULL AND
    SeatAttribute_floor.deleted_at IS NULL AND
    SeatAttribute_gate.deleted_at IS NULL
    ;
""")

def downgrade():
    op.drop_table('L0Seat')
