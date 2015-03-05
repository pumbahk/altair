"""add_error_type_to_sej_order

Revision ID: 287cb4bede2b
Revises: 1261b43ea7c7
Create Date: 2015-03-01 20:08:16.027156

"""

# revision identifiers, used by Alembic.
revision = '287cb4bede2b'
down_revision = '1261b43ea7c7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''ALTER TABLE SejOrder ADD COLUMN error_type INTEGER;''')

def downgrade():
    op.execute('''ALTER TABLE SejOrder DROP COLUMN error_type;''')
