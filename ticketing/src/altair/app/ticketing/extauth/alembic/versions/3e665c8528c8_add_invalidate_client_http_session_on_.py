"""add_invalidate_client_http_session_on_access_token_revocation_to_organization

Revision ID: 3e665c8528c8
Revises: 582d09a3f38d
Create Date: 2015-11-16 13:45:20.259911

"""

# revision identifiers, used by Alembic.
revision = '3e665c8528c8'
down_revision = '582d09a3f38d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Organization', sa.Column('invalidate_client_http_session_on_access_token_revocation', sa.Boolean(), nullable=False, server_default=text('FALSE')))

def downgrade():
    op.drop_column('Organization', 'invalidate_client_http_session_on_access_token_revocation')
