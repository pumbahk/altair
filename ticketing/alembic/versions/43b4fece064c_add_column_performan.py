"""add column Performance.public

Revision ID: 43b4fece064c
Revises: 49e6fa971a5
Create Date: 2012-10-30 17:20:08.677807

"""

# revision identifiers, used by Alembic.
revision = '43b4fece064c'
down_revision = '49e6fa971a5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('Performance', sa.Column('public', sa.Boolean(), nullable=False, default=False, server_default=text('0')))
    op.execute("UPDATE Performance SET public = 1 WHERE deleted_at IS NULL")

def downgrade():
    op.drop_column('Performance', 'public')

