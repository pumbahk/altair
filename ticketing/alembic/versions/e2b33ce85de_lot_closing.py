"""lot closing

Revision ID: e2b33ce85de
Revises: 3c09f04450b3
Create Date: 2013-06-17 11:15:08.554481

"""

# revision identifiers, used by Alembic.
revision = 'e2b33ce85de'
down_revision = '3c09f04450b3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('LotEntry',
                  sa.Column("closed_at", sa.DateTime))

def downgrade():
    op.drop_column('LotEntry','closed_at')
