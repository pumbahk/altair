"""remove_duplicate_constraint

Revision ID: 2d3bab513d5
Revises: 3aa73a04193d
Create Date: 2012-11-08 14:30:01.319347

"""

# revision identifiers, used by Alembic.
revision = '2d3bab513d5'
down_revision = '3aa73a04193d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.drop_constraint('VenueArea_group_l0_id_ibfk_1', 'VenueArea_group_l0_id', type='foreignkey')

def downgrade():
    op.create_foreign_key('VenueArea_group_l0_id_ibfk_1', 'VenueArea_group_l0_id', 'Venue', ['venue_id'], ['id'])
