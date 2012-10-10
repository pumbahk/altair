"""drop_last_issued_at

Revision ID: 2aa4d646b5fd
Revises: 46c057f3d463
Create Date: 2012-10-10 13:13:41.573957

"""

# revision identifiers, used by Alembic.
revision = '2aa4d646b5fd'
down_revision = '46c057f3d463'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("UPDATE `Order` SET issued_at=last_issued_at WHERE last_issued_at IS NOT NULL AND issued_at iS NULL")
    op.drop_column("Order", "last_issued_at")

def downgrade():
    op.add_column('Order', sa.Column('last_issued_at', sa.TIMESTAMP(), default=None, nullable=True))
    op.execute("UPDATE `Order` SET last_issued_at=issued_at")
