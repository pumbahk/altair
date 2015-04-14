"""add visible to PerformanceSetting

Revision ID: 26aa199ca459
Revises: 18b5da6a9ed5
Create Date: 2015-04-07 16:26:21.040438

"""

# revision identifiers, used by Alembic.
revision = '26aa199ca459'
down_revision = '18b5da6a9ed5'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('PerformanceSetting', sa.Column('visible', sa.Boolean(), nullable=False, default=True, server_default='1'))

def downgrade():
    op.drop_column('PerformanceSetting', 'visible')
