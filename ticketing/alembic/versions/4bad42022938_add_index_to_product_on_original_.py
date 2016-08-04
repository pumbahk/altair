"""add index to Product on original_product_id

Revision ID: 4bad42022938
Revises: 209707809135
Create Date: 2016-08-04 16:09:16.086692

"""

# revision identifiers, used by Alembic.
revision = '4bad42022938'
down_revision = '209707809135'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_index('original_product_id', 'Product', ['original_product_id'])

def downgrade():
    op.drop_index('original_product_id', 'Product')
