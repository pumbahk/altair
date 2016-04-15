"""add ordered_product_item_token_id column to SejTicket

Revision ID: 1cc638e76055
Revises: 1173311eb7c3
Create Date: 2016-04-13 17:55:56.242808

"""

# revision identifiers, used by Alembic.
revision = '1cc638e76055'
down_revision = '1173311eb7c3'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger



def upgrade():
    op.add_column('SejTicket', sa.Column('ordered_product_item_token_id', Identifier(), nullable=True))

def downgrade():
    op.drop_column(u'SejTicket', 'ordered_product_item_token_id')
