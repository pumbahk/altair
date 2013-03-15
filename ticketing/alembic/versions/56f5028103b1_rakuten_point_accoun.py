"""rakuten_point_account

Revision ID: 56f5028103b1
Revises: 17d62e30cb0d
Create Date: 2013-03-15 10:09:23.804326

"""

# revision identifiers, used by Alembic.
revision = '56f5028103b1'
down_revision = '17d62e30cb0d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column("UserProfile",
                  sa.Column("rakuten_point_account", sa.String(20))
    )

def downgrade():
    op.drop_column('UserProfile', 'rakuten_point_account')
