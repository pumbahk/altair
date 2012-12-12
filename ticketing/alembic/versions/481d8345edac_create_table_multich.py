"""create table multicheckout_request_card_sales_part_cancel

Revision ID: 481d8345edac
Revises: 54d62937d132
Create Date: 2012-11-29 20:51:51.391131

"""

# revision identifiers, used by Alembic.
revision = '481d8345edac'
down_revision = 'b43ac6db823'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('multicheckout_request_card_sales_part_cancel',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('SalesAmountCancellation', sa.Integer(), nullable=True),
        sa.Column('TaxCarriageCancellation', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
        )

def downgrade():
    op.drop_table('multicheckout_request_card_sales_part_cancel')

