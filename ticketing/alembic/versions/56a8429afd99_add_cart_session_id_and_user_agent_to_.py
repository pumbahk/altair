"""add_cart_session_id_and_user_agent_to_lot_entry

Revision ID: 56a8429afd99
Revises: 1a448cfe9a8d
Create Date: 2015-02-27 17:59:18.725983

"""

# revision identifiers, used by Alembic.
revision = '56a8429afd99'
down_revision = '1a448cfe9a8d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
        op.execute('ALTER TABLE LotEntry ADD COLUMN cart_session_id BINARY(72) NOT NULL, ADD COLUMN user_agent BINARY(200) NOT NULL');

def downgrade():
    pass
