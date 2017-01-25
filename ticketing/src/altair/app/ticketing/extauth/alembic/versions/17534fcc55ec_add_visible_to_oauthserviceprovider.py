"""Add visible to OAuthServiceProvider

Revision ID: 17534fcc55ec
Revises: 38a51a4056bf
Create Date: 2017-01-25 13:17:34.973913

"""

# revision identifiers, used by Alembic.
revision = '17534fcc55ec'
down_revision = '38a51a4056bf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OAuthServiceProvider', sa.Column('visible', sa.Boolean(), nullable=False, server_default='1'))

def downgrade():
    op.drop_column('OAuthServiceProvider', 'visible')
