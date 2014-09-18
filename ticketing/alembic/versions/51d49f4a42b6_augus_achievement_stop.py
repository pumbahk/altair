"""augus_achievement_stop

Revision ID: 51d49f4a42b6
Revises: 2c844ed2c11
Create Date: 2014-09-18 17:42:43.671467

"""

# revision identifiers, used by Alembic.
revision = '51d49f4a42b6'
down_revision = '2c844ed2c11'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column(
        'AugusPerformance',
        sa.Column('stoped_at', sa.TIMESTAMP(), nullable=True),
        )

def downgrade():
    op.drop_column('AugusPerformance', 'stoped_at')
