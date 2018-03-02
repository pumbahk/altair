# -*- coding: utf-8 -*-
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
    # 今回追加したカラムは、後日op.alter_column()でnullableをTrueに変更する
    op.add_column('UsedDiscountCodeCart', sa.Column('discount_code_setting_id', Identifier, nullable=True))
    op.add_column('UsedDiscountCodeCart', sa.Column('applied_amount', sa.Integer(8), nullable=True))
    op.add_column('UsedDiscountCodeCart', sa.Column('benefit_amount', sa.Integer(8), nullable=True))
    op.add_column('UsedDiscountCodeCart', sa.Column('benefit_unit', sa.Unicode(1), nullable=True))

    op.add_column('UsedDiscountCodeOrder', sa.Column('discount_code_setting_id', Identifier, nullable=True))
    op.add_column('UsedDiscountCodeOrder', sa.Column('applied_amount', sa.Integer(8), nullable=True))
    op.add_column('UsedDiscountCodeOrder', sa.Column('benefit_amount', sa.Integer(8), nullable=True))
    op.add_column('UsedDiscountCodeOrder', sa.Column('benefit_unit', sa.Unicode(1), nullable=True))


def downgrade():
    op.drop_column('UsedDiscountCodeCart', 'discount_code_setting_id')
    op.drop_column('UsedDiscountCodeCart', 'applied_amount')
    op.drop_column('UsedDiscountCodeCart', 'benefit_amount')
    op.drop_column('UsedDiscountCodeCart', 'benefit_unit')

    op.drop_column('UsedDiscountCodeOrder', 'discount_code_setting_id')
    op.drop_column('UsedDiscountCodeOrder', 'applied_amount')
    op.drop_column('UsedDiscountCodeOrder', 'benefit_amount')
    op.drop_column('UsedDiscountCodeOrder', 'benefit_unit')
