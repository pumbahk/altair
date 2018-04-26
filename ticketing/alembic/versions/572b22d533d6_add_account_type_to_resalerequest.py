"""add account type to ResaleRequest

Revision ID: 572b22d533d6
Revises: 2f6a5a0b914b
Create Date: 2018-04-19 15:25:28.470945

"""

# revision identifiers, used by Alembic.
revision = '572b22d533d6'
down_revision = '2f6a5a0b914b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('ResaleRequest', sa.Column('account_type', sa.Unicode(64), nullable=False, server_default=''))

def downgrade():
    op.drop_column('ResaleRequest', 'account_type')
