"""add_unit_value_code

Revision ID: 521506639053
Revises: 2cda4724cc40
Create Date: 2014-02-18 10:24:37.310366

"""

# revision identifiers, used by Alembic.
revision = '521506639053'
down_revision = '2cda4724cc40'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('AugusTicket',
                  sa.Column('unit_value_code', sa.Integer(), nullable=False))
    op.execute('UPDATE `AugusTicket` SET unit_value_code=0')

def downgrade():
    op.drop_column('AugusTicket', 'unit_value_code')
