"""create_index_on_order_no_multicheckout_response_card

Revision ID: 3929f09d49fb
Revises: 7657f6f6b68
Create Date: 2014-12-18 12:01:13.838833

"""

# revision identifiers, used by Alembic.
revision = '3929f09d49fb'
down_revision = '7657f6f6b68'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('ix_OrderNo', 'multicheckout_response_card', ['OrderNo'])

def downgrade():
    op.drop_index('ix_OrderNo', 'multicheckout_response_card')
