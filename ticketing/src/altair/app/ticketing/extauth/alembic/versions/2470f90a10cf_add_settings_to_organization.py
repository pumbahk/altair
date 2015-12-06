"""add_settings_to_organization

Revision ID: 2470f90a10cf
Revises: 13cc3341b9d5
Create Date: 2015-11-09 18:21:38.276850

"""

# revision identifiers, used by Alembic.
revision = '2470f90a10cf'
down_revision = '13cc3341b9d5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from altair.models import MutationDict, JSONEncodedDict

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('settings', MutationDict.as_mutable(JSONEncodedDict(2048))))


def downgrade():
    op.drop_column('Organization', 'settings')
