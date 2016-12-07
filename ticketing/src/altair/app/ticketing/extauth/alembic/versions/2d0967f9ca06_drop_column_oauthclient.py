"""drop column OAuthClient

Revision ID: 2d0967f9ca06
Revises: ebba25add85
Create Date: 2016-10-19 16:35:22.928266

"""

# revision identifiers, used by Alembic.
revision = '2d0967f9ca06'
down_revision = 'ebba25add85'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column(u'OAuthClient', 'valid_since')
    op.drop_column(u'OAuthClient', 'expire_at')
    op.drop_column(u'Organization', 'maximum_oauth_client_expiration_time')

def downgrade():
    op.add_column('OAuthClient', sa.Column('valid_since', sa.DateTime(), nullable=True))
    op.add_column('OAuthClient', sa.Column('expire_at', sa.DateTime(), nullable=True))
    op.add_column('Organization', sa.Column('maximum_oauth_client_expiration_time', sa.Int(), default=63072000, nullable=False))
