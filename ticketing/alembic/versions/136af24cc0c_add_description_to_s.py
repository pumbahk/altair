"""add_description_to_stock_type_and_product

Revision ID: 136af24cc0c
Revises: 85564a50acf
Create Date: 2013-01-04 17:18:15.308666

"""

# revision identifiers, used by Alembic.
revision = '136af24cc0c'
down_revision = '85564a50acf'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('StockType', sa.Column('description', sa.String(2000)))
    op.add_column('Product', sa.Column('description', sa.String(2000)))

def downgrade():
    op.drop_column('StockType', 'description')
    op.drop_column('Product', 'description')
