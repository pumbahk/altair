"""add_cart_session_id_and_user_agent_to_lot_entry

Revision ID: 56a8429afd99
Revises: 34ecd9a19da2
Create Date: 2015-02-27 17:59:18.725983

"""

# revision identifiers, used by Alembic.
revision = '56a8429afd99'
down_revision = '34ecd9a19da2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""ALTER TABLE LotEntry ADD COLUMN cart_session_id VARBINARY(72) NOT NULL DEFAULT '', ADD COLUMN user_agent VARBINARY(200) NOT NULL DEFAULT '';""")


def downgrade():
    op.execute('ALTER TABLE LotEntry DROP COLUMN cart_session_id, DROP COLUMN user_agent')
