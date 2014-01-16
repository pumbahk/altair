"""alter table Lot add column lotting_announce_timezone, custom_timezone_label

Revision ID: 493be3f09c7a
Revises: f17612db378
Create Date: 2014-01-16 11:12:06.216916

"""

# revision identifiers, used by Alembic.
revision = '493be3f09c7a'
down_revision = 'f17612db378'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Lot', sa.Column('lotting_announce_timezone', sa.Unicode(length=255), nullable=True))
    op.add_column('Lot', sa.Column('custom_timezone_label', sa.Unicode(length=255), nullable=True))

def downgrade():
    op.drop_column('Lot', u'lotting_announce_timezone')
    op.drop_column('Lot', u'custom_timezone_label')