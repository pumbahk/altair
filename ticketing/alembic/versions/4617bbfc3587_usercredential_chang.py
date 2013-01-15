"""UserCredential change constraint

Revision ID: 4617bbfc3587
Revises: 7155803f136
Create Date: 2013-01-10 16:47:23.563097

"""

# revision identifiers, used by Alembic.
revision = '136af24cc0c'
down_revision = '7155803f136'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE UserCredential DROP INDEX auth_identifier;");
    op.execute("ALTER TABLE UserCredential ADD UNIQUE ib_unique_1 (auth_identifier, membership_id, deleted_at);")


def downgrade():
    op.execute("ALTER TABLE UserCredential DROP INDEX ib_unique_1;")
    op.execute("ALTER TABLE UserCredential ADD UNIQUE auth_identifier (auth_identifier);")
