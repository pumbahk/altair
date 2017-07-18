"""add index to LotEntry

Revision ID: 3b9d24020871
Revises: 34a630c1fee0
Create Date: 2017-07-14 13:49:40.141507

"""

# revision identifiers, used by Alembic.
revision = '3b9d24020871'
down_revision = '34a630c1fee0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('LotEntry_ibfk_10', 'LotEntry', ['created_at'])

def downgrade():
    op.drop_index('LotEntry_ibfk_10', 'LotEntry')
