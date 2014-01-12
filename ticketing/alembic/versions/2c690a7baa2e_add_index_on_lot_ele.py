"""add_index_on_lot_elect_work

Revision ID: 2c690a7baa2e
Revises: 1493b4cccc04
Create Date: 2014-01-12 23:10:30.542163

"""

# revision identifiers, used by Alembic.
revision = '2c690a7baa2e'
down_revision = '1493b4cccc04'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('entry_wish_no', 'LotElectWork', ['entry_wish_no'])

def downgrade():
    op.drop_index('entry_wish_no', 'LotElectWork')
