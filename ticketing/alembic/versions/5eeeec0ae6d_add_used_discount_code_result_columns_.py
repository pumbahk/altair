"""add_used_discount_code_result_columns_on_cart_and_order

Revision ID: 5eeeec0ae6d
Revises: 4c5235a1dea8
Create Date: 2018-02-28 13:59:06.336436

"""

# revision identifiers, used by Alembic.
revision = '5eeeec0ae6d'
down_revision = '4c5235a1dea8'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    pass

def downgrade():
    pass
