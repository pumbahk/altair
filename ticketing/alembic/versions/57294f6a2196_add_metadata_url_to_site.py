"""add_data_to_site

Revision ID: 57294f6a2196
Revises: 362dc10402f5
Create Date: 2012-09-12 16:24:33.110909

"""

# revision identifiers, used by Alembic.
revision = '57294f6a2196'
down_revision = '362dc10402f5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Site', sa.Column('metadata_url', sa.String(255)))

def downgrade():
    op.drop_column('Site', 'metadata_url')
