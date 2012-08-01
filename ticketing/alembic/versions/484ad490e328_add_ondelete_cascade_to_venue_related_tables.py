"""add_ondelete_cascades_to_venue_related_tables

Revision ID: 484ad490e328
Revises: 35b86939aab4
Create Date: 2012-07-30 11:55:18.148471

"""

# revision identifiers, used by Alembic.
revision = '484ad490e328'
down_revision = '35b86939aab4'

from alembic import op
import sqlalchemy as sa

def modify_foreign_key(name, source, referent, local_cols, remote_cols, onupdate=None, ondelete=None):
    try:
        op.drop_constraint(name, source, 'foreignkey')
    except:
        pass
    op.create_foreign_key(
        name=name,
        source=source,
        referent=referent,
        local_cols=local_cols,
        remote_cols=remote_cols,
        onupdate=onupdate,
        ondelete=ondelete
        )

def do(_):
    _('seat_ibfk_3', 'Seat', 'Venue', ['venue_id'], ['id']) 
    _('seatadjacencyset_ibfk_1', 'SeatAdjacencySet', 'Venue', ['venue_id'], ['id']) 
    _('seatadjacency_ibfk_1', 'SeatAdjacency', 'SeatAdjacencySet', ['adjacency_set_id'], ['id']) 
    _('seat_seatadjacency_ibfk_1', 'Seat_SeatAdjacency', 'Seat', ['seat_id'], ['id'])
    _('seat_seatadjacency_ibfk_2', 'Seat_SeatAdjacency', 'SeatAdjacency', ['seat_adjacency_id'], ['id'])
    _('seatstatus_ibfk_1', 'SeatStatus', 'Seat', ['seat_id'], ['id'])
    _('seatattribute_ibfk_1', 'SeatAttribute', 'Seat', ['seat_id'], ['id'])
    _('seatindextype_ibfk_1', 'SeatIndexType', 'Venue', ['venue_id'], ['id'])
    _('seatindex_ibfk_1', 'SeatIndex', 'Seat', ['seat_id'], ['id'])
    _('seatindex_ibfk_2', 'SeatIndex', 'SeatIndexType', ['seat_index_type_id'], ['id'])
    _('venuearea_group_l0_id_ibfk_2', 'VenueArea_group_l0_id', 'VenueArea', ['venue_area_id'], ['id'])
    _('venuearea_group_l0_id_ibfk_3', 'VenueArea_group_l0_id', 'Venue', ['venue_id'], ['id'])
    _('venue_ibfk_1', 'Venue', 'Organization', ['organization_id'], ['id'])
    _('venue_ibfk_3', 'Venue', 'Performance', ['performance_id'], ['id'])
    _('venue_ibfk_4', 'Venue', 'Site', ['site_id'], ['id'])

def upgrade():
    def add_ondelete(*args):
        modify_foreign_key(*args, ondelete='CASCADE')
    do(add_ondelete)

def downgrade():
    def remove_ondelete(*args):
        modify_foreign_key(*args, ondelete=None)
    do(remove_ondelete)
