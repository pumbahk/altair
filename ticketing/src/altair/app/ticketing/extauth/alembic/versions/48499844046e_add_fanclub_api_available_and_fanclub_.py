"""add_fanclub_api_available_and_fanclub_api_type_to_extauth_organization

Revision ID: 48499844046e
Revises: 277863733337
Create Date: 2016-01-15 22:47:49.978506

"""

# revision identifiers, used by Alembic.
revision = '48499844046e'
down_revision = '277863733337'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('fanclub_api_available', sa.Boolean(), nullable=False, default=False, server_default=text("FALSE")))
    op.add_column('Organization', sa.Column('fanclub_api_type', sa.Unicode(32), nullable=True, default=None, server_default=text("NULL")))
    op.execute("""UPDATE Organization SET fanclub_api_available=TRUE, fanclub_api_type='eagles' WHERE Organization.canonical_host_name LIKE 'eagles.%';""")

def downgrade():
    op.drop_column('Organization', 'fanclub_api_type')
    op.drop_column('Organization', 'fanclub_api_available')
