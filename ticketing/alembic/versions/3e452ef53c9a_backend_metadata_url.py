"""backend_metadata_url

Revision ID: 3e452ef53c9a
Revises: 32e91f11f5af
Create Date: 2013-05-28 12:19:06.034154

"""

# revision identifiers, used by Alembic.
revision = '3e452ef53c9a'
down_revision = '32e91f11f5af'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('Site', sa.Column('backend_metadata_url', sa.Unicode(255), nullable=True))

def downgrade():
    op.drop_column('Site', 'backend_metadata_url')
