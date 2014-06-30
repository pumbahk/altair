"""update Order.released_at

Revision ID: 582ff2b52a2b
Revises: 141f7ed1cda4
Create Date: 2014-06-16 10:45:39.228659

"""

# revision identifiers, used by Alembic.
revision = '582ff2b52a2b'
down_revision = '141f7ed1cda4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("UPDATE `Order` SET released_at = refunded_at, updated_at = now() WHERE released_at IS NULL AND refunded_at IS NOT NULL AND refunded_at < '2014-06-05 04:00:00' AND canceled_at IS NULL AND deleted_at IS NULL")

def downgrade():
    op.execute("UPDATE `Order` SET released_at = NULL, updated_at = now() WHERE released_at IS NOT NULL AND refunded_at IS NOT NULL AND refunded_at < '2014-06-05 04:00:00' AND canceled_at IS NULL AND deleted_at IS NULL")
