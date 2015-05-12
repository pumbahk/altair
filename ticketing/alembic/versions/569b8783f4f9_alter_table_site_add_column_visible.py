"""alter table Site add column visible

Revision ID: 569b8783f4f9
Revises: 10ffc65de6c5
Create Date: 2015-05-12 10:41:31.431607

"""

# revision identifiers, used by Alembic.
revision = '569b8783f4f9'
down_revision = '10ffc65de6c5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('Site', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))

def downgrade():
    op.drop_column('Site', 'visible')

