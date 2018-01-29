"""alter table UsedDiscountCodeOrder add column ordered_product_item_token_id

Revision ID: 230af9e45f4e
Revises: 1bf3716c54c2
Create Date: 2017-12-26 14:37:15.370504

"""

# revision identifiers, used by Alembic.
revision = '230af9e45f4e'
down_revision = '1bf3716c54c2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('UsedDiscountCodeOrder', sa.Column('ordered_product_item_token_id', Identifier))
    op.create_foreign_key('UsedDiscountCodeOrder_ibfk_3', 'UsedDiscountCodeOrder', 'OrderedProductItemToken', ['ordered_product_item_token_id'], ['id'])


def downgrade():
    op.drop_constraint('UsedDiscountCodeOrder_ibfk_3', 'UsedDiscountCodeOrder', type_='foreignkey')
    op.drop_column(u'UsedDiscountCodeOrder', 'ordered_product_item_token_id')
