"""input_start_at_data_for_sports_service

Revision ID: daa86477ebb
Revises: 2cd4d21b8402
Create Date: 2018-03-06 17:12:00.618982

"""

# revision identifiers, used by Alembic.
revision = 'daa86477ebb'
down_revision = '2cd4d21b8402'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute('''
               UPDATE `DiscountCodeSetting` dcs
               SET dcs.start_at = '2018-02-24 10:00:00'
               WHERE dcs.start_at IS NULL
                 AND dcs.issued_by = 'sports_service'
               ''')

def downgrade():
    pass
