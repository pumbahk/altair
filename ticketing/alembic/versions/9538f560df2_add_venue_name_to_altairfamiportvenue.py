"""Add venue_name to AltairFamiPortVenue

Revision ID: 9538f560df2
Revises: 38b6b43b7e5d
Create Date: 2015-12-21 13:07:16.022593

"""

# revision identifiers, used by Alembic.
revision = '9538f560df2'
down_revision = '2ad439355691'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('AltairFamiPortVenue', sa.Column('venue_name', sa.Unicode(50), nullable=False))
    op.execute('UPDATE AltairFamiPortVenue SET venue_name = name, updated_at = now() WHERE id = id')

def downgrade():
    op.drop_column('AltairFamiPortVenue', 'venue_name')
