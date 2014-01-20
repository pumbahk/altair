"""augus_venue_drop_constraint

Revision ID: f17612db378
Revises: ef8cf89c891
Create Date: 2014-01-15 17:49:51.216782

"""

# revision identifiers, used by Alembic.
revision = 'f17612db378'
down_revision = 'ef8cf89c891'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.drop_constraint('venue_id', 'AugusVenue', type='unique')

def downgrade():
    op.create_unique_constraint('venue_id', 'AugusVenue', ['venue_id'])


