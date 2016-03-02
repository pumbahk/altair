"""Create AltairFamiPortVenue_Venue table

Revision ID: 1173311eb7c3
Revises: 32d04da45742
Create Date: 2016-02-24 13:15:42.092269

"""

# revision identifiers, used by Alembic.
revision = '1173311eb7c3'
down_revision = '32d04da45742'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('AltairFamiPortVenue_Venue',
        sa.Column('altair_famiport_venue_id', Identifier, sa.ForeignKey('AltairFamiPortVenue.id', ondelete='CASCADE'), nullable=False),
        sa.Column('venue_id', Identifier, sa.ForeignKey('Venue.id', ondelete='CASCADE'), nullable=False),
        sa.PrimaryKeyConstraint('altair_famiport_venue_id', 'venue_id')
        )

    # Set up AltairFamiPortVenue_Venue based on existing data in AltairFamiPortVenue_Site
    insert_sql = u"INSERT INTO AltairFamiPortVenue_Venue (altair_famiport_venue_id, venue_id) \
                   SELECT DISTINCT a_s.altair_famiport_venue_id, v.id FROM AltairFamiPortVenue_Site as a_s \
                   INNER JOIN AltairFamiPortPerformanceGroup as afmpg ON a_s.altair_famiport_venue_id = afmpg.altair_famiport_venue_id \
                   INNER JOIN AltairFamiPortPerformance as afmp ON afmpg.id = afmp.altair_famiport_performance_group_id \
                   INNER JOIN Venue as v ON v.performance_id = afmp.performance_id"
    op.execute(insert_sql)

def downgrade():
    op.drop_table('AltairFamiPortVenue_Venue')
