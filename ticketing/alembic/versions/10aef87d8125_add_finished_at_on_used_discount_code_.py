"""add_finished_at_on_used_discount_code_cart

Revision ID: 10aef87d8125
Revises: 230af9e45f4e
Create Date: 2018-01-10 23:02:16.943173

"""

# revision identifiers, used by Alembic.
revision = '10aef87d8125'
down_revision = '230af9e45f4e'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger

def upgrade():
    op.add_column('UsedDiscountCodeCart', sa.Column('finished_at', sa.DateTime(), nullable=True))

def downgrade():
    op.drop_column('UsedDiscountCodeCart', 'finished_at')
