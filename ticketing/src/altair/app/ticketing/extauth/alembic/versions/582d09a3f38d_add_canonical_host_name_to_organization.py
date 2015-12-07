"""add_canonical_host_name_to_organization

Revision ID: 582d09a3f38d
Revises: 2470f90a10cf
Create Date: 2015-11-16 10:35:30.027846

"""

# revision identifiers, used by Alembic.
revision = '582d09a3f38d'
down_revision = '2470f90a10cf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('canonical_host_name', sa.Unicode(128), sa.ForeignKey('Host.host_name'), nullable=True))
    op.execute("UPDATE Organization JOIN Host ON Organization.id=Host.organization_id SET Organization.canonical_host_name=Host.host_name;")

def downgrade():
    op.drop_constraint('Organization_ibfk_1', 'Organization', type_='foreignkey')
    op.drop_column('Organization', 'canonical_host_name')
