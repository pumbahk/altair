"""genre has origin

Revision ID: dd1556bd98a
Revises: 16f22b03e96
Create Date: 2013-03-14 10:28:59.595470

"""

# revision identifiers, used by Alembic.
revision = 'dd1556bd98a'
down_revision = '16f22b03e96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column("genre", sa.Column("origin", sa.String(length=32), nullable=True))

def downgrade():
    op.drop_column("genre", "origin")
