"""drop column LotElectWork.deleted_at

Revision ID: f65df8d40c7
Revises: 2e1379ff8b2c
Create Date: 2014-04-23 14:47:09.009674

"""

# revision identifiers, used by Alembic.
revision = 'f65df8d40c7'
down_revision = '2e1379ff8b2c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.drop_column(u'LotElectWork', 'deleted_at')

def downgrade():
    op.add_column(u'LotElectWork', sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True))
