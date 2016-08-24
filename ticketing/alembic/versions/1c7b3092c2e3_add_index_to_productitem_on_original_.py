"""add index to ProductItem on original_product_item_id

Revision ID: 1c7b3092c2e3
Revises: 4bad42022938
Create Date: 2016-08-04 16:09:43.092249

"""

# revision identifiers, used by Alembic.
revision = '1c7b3092c2e3'
down_revision = '4bad42022938'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('original_product_item_id', 'ProductItem', ['original_product_item_id'])

def downgrade():
    op.drop_index('original_product_item_id', 'ProductItem')
