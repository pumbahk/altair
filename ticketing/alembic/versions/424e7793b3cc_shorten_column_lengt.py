"""shorten_column_lengths

Revision ID: 424e7793b3cc
Revises: 148ac8e356cc
Create Date: 2013-07-24 14:59:11.873066

"""

# revision identifiers, used by Alembic.
revision = '424e7793b3cc'
down_revision = '148ac8e356cc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def shorten_column_length(tablename, indexname, columnname, type_, nullable=True):
    if indexname is not None:
        try:
            op.drop_index(indexname, tablename)
        except:
            pass
    op.alter_column(tablename, columnname, type_=type_, existing_nullable=nullable)
    if indexname is not None:
        op.create_index(indexname, tablename, [columnname], mysql_length=min(64, type_.length))

COLUMNS = [
    ('Seat', 'ix_Seat_group_l0_id', 'group_l0_id', sa.Unicode, 48, 255, True, []),
    ('Seat', 'ix_row_l0_id', 'row_l0_id', sa.Unicode, 48, 255, True, []),
    ]

def modify_Seat_l0_id_length(n, revert=False):
    op.drop_constraint('Seat_SeatAdjacency2_ibfk_2', 'Seat_SeatAdjacency2', type='foreignkey')
    op.drop_index('PRIMARY', 'Seat_SeatAdjacency2')
    op.drop_index('ix_Seat_l0_id', 'Seat')
    op.alter_column('Seat_SeatAdjacency2', 'l0_id', type_=sa.Unicode(n), existing_nullable=False)
    op.alter_column('Seat', 'l0_id', type_=sa.Unicode(n), nullable=False)
    opts = {}
    if not revert:
        opts['mysql_length'] = min(64, n)
    op.create_index('ix_Seat_l0_id', 'Seat', ['l0_id'], **opts)
    op.create_primary_key(None, 'Seat_SeatAdjacency2', ['l0_id', 'seat_adjacency_id'])
    op.create_foreign_key('Seat_SeatAdjacency2_ibfk_2', 'Seat_SeatAdjacency2', 'Seat', ['l0_id'], ['l0_id'], ondelete='CASCADE')

def modify_VenueArea_group_l0_id_length(n, revert=False):
    op.drop_constraint('VenueArea_group_l0_id_ibfk_3', 'VenueArea_group_l0_id', type='foreignkey')
    op.drop_index('PRIMARY', 'VenueArea_group_l0_id')
    op.drop_index('group_l0_id', 'VenueArea_group_l0_id')
    op.alter_column('VenueArea_group_l0_id', 'group_l0_id', type_=sa.Unicode(n), existing_nullable=False)
    op.create_primary_key(None, 'VenueArea_group_l0_id', ['venue_id', 'group_l0_id', 'venue_area_id'])
    opts = {}
    if not revert:
        opts['mysql_length'] = min(64, n)
    op.create_index('group_l0_id', 'VenueArea_group_l0_id', ['group_l0_id'], **opts)
    op.create_foreign_key('VenueArea_group_l0_id_ibfk_3', 'VenueArea_group_l0_id', 'Venue', ['venue_id'], ['id'], ondelete='CASCADE')

def upgrade():
    for tablename, indexname, columnname, type_, length, _, existing_nullable, foreign_key_constraints in COLUMNS:
        for foreign_key_constraint in foreign_key_constraints:
            op.drop_constraint(foreign_key_constraint[0], foreign_key_constraint[1], type='foreignkey')
        shorten_column_length(tablename, indexname, columnname, type_(length), existing_nullable)
        for foreign_key_constraint in foreign_key_constraints:
            op.create_foreign_key(foreign_key_constraint[0], foreign_key_constraint[1], tablename, foreign_key_constraint[2], foreign_key_constraint[3])

    modify_Seat_l0_id_length(48)
    modify_VenueArea_group_l0_id_length(48)

def downgrade():
    modify_VenueArea_group_l0_id_length(255, True)
    modify_Seat_l0_id_length(255, True)

    for tablename, indexname, columnname, type_, _, length, existing_nullable, foreign_key_constraints in reversed(COLUMNS):
        for foreign_key_constraint in foreign_key_constraints:
            op.drop_constraint(foreign_key_constraint[0], foreign_key_constraint[1], type='foreignkey')
        shorten_column_length(tablename, indexname, columnname, type_(length), existing_nullable)
        for foreign_key_constraint in foreign_key_constraints:
            op.create_foreign_key(foreign_key_constraint[0], foreign_key_constraint[1], tablename, foreign_key_constraint[2], foreign_key_constraint[3])
