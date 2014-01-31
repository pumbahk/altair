"""birth_day_to_birthday

Revision ID: 23dc7707136d
Revises: 408ad74d00ea
Create Date: 2014-01-31 12:01:42.917147

"""

# revision identifiers, used by Alembic.
revision = '23dc7707136d'
down_revision = '408ad74d00ea'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('UserProfile', sa.Column('birthday', sa.Date(), nullable=True))
    op.execute('UPDATE UserProfile SET birthday=birth_day')

def downgrade():
    op.drop_column('UserProfile', 'birthday')
