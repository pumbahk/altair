"""alter table Seat add column original_seat_id

Revision ID: 553d9a30af4a
Revises: 2788e072c710
Create Date: 2013-04-17 14:35:28.329482

"""

# revision identifiers, used by Alembic.
revision = '553d9a30af4a'
down_revision = '2788e072c710'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("CREATE TABLE Seat_SeatAdjacency2 SELECT l0_id, seat_adjacency_id FROM Seat_SeatAdjacency JOIN Seat ON Seat_SeatAdjacency.seat_id=Seat.id JOIN Venue ON Seat.venue_id=Venue.id WHERE Venue.original_venue_id IS NULL AND Venue.deleted_at IS NULL")
    op.execute("ALTER TABLE Seat_SeatAdjacency2 ADD PRIMARY KEY (l0_id, seat_adjacency_id)")
    op.create_foreign_key(u'Seat_SeatAdjacency2_ibfk_1', 'Seat_SeatAdjacency2', 'SeatAdjacency', ['seat_adjacency_id'], ['id'])

    op.add_column(u'SeatAdjacencySet', sa.Column('site_id', Identifier))
    op.create_foreign_key(u'SeatAdjacencySet_ibfk_2', 'SeatAdjacencySet', 'Site', ['site_id'], ['id'], ondelete='CASCADE')
    op.execute("UPDATE SeatAdjacencySet sas, Venue v SET sas.site_id = v.site_id WHERE sas.venue_id = v.id AND v.original_venue_id IS NULL AND v.deleted_at IS NULL")

def downgrade():
    op.drop_constraint(u'SeatAdjacencySet_ibfk_2', u'SeatAdjacencySet', type="foreignkey")
    op.drop_column(u'SeatAdjacencySet', 'site_id')

    op.drop_constraint(u'Seat_SeatAdjacency2_ibfk_1', u'Seat_SeatAdjacency2', type="foreignkey")
    op.drop_table("Seat_SeatAdjacency2")
