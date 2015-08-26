"""add_altair_famiport_venue_site_table

Revision ID: 20f37ac7246d
Revises: 19401e2f1852
Create Date: 2015-08-26 01:26:22.360368

"""

# revision identifiers, used by Alembic.
revision = '20f37ac7246d'
down_revision = '19401e2f1852'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('AltairFamiPortVenue_Site',
        sa.Column('altair_famiport_venue_id', Identifier, sa.ForeignKey('AltairFamiPortVenue.id', ondelete='CASCADE'), nullable=False),
        sa.Column('site_id', Identifier, sa.ForeignKey('Site.id', ondelete='CASCADE'), nullable=False),
        sa.PrimaryKeyConstraint('altair_famiport_venue_id', 'site_id')
        )
    op.execute('INSERT INTO AltairFamiPortVenue_Site (altair_famiport_venue_id, site_id) SELECT id altair_famiport_venue_id, site_id FROM AltairFamiPortVenue;')
    op.drop_constraint('AltairFamiPortVenue_ibfk_2', 'AltairFamiPortVenue', type_='foreignkey')
    op.drop_column('AltairFamiPortVenue', 'site_id')
    op.alter_column('AltairFamiPortVenue', 'famiport_venue_id', nullable=True, existing_type=Identifier)

def downgrade():
    op.alter_column('AltairFamiPortVenue', 'famiport_venue_id', nullable=False, existing_type=Identifier)
    op.add_column('AltairFamiPortVenue', sa.Column('site_id', Identifier, sa.ForeignKey('Site.id')))
    op.execute('UPDATE AltairFamiPortVenue JOIN AltairFamiPortVenue_Site ON AltairFamiPortVenue.id=AltairFamiPortVenue_Site.altair_famiport_venue_id SET AltairFamiPortVenue.site_id=AltairFamiPortVenue_Site.site_id;')
    op.drop_table('AltairFamiPortVenue_Site')

