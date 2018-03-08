"""add_data_on_empty_columns_on_used_discount_codes

Revision ID: 2cd4d21b8402
Revises: 5eeeec0ae6d
Create Date: 2018-03-05 11:34:55.452027

"""

# revision identifiers, used by Alembic.
revision = '2cd4d21b8402'
down_revision = '5eeeec0ae6d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    """
    Update UsedDiscountCodeCart and UsedDiscountCodeOrder tables.
    Except for the records which already have discount_code_setting_id.
    Those records are created after TKT5040 was released.
    :return: void
    """
    op.execute('''
               UPDATE `UsedDiscountCodeCart` udcc,
                      `CartedProductItem` cpi,
                      `CartedProduct` cp,
                      `Product` p,
                      `DiscountCodeSetting` dcs
               SET udcc.applied_amount = p.price,
                   udcc.discount_code_setting_id = dcs.id,
                   udcc.benefit_amount = dcs.benefit_amount,
                   udcc.benefit_unit = dcs.benefit_unit
               WHERE udcc.carted_product_item_id = cpi.id
                 AND cpi.carted_product_id = cp.id
                 AND cp.product_id = p.id
                 AND udcc.discount_code_setting_id IS NULL
                 AND dcs.first_digit = SUBSTRING(udcc.code FROM 1 FOR 1)
                 AND dcs.following_2to4_digits = SUBSTRING(udcc.code FROM 2 FOR 3)
                 AND dcs.deleted_at IS NULL
               ''')

    op.execute('''
               UPDATE `UsedDiscountCodeOrder` udco,
                      `OrderedProductItem` opi,
                      `DiscountCodeSetting` dcs
               SET udco.applied_amount = opi.price,
                   udco.discount_code_setting_id = dcs.id,
                   udco.benefit_amount = dcs.benefit_amount,
                   udco.benefit_unit = dcs.benefit_unit
               WHERE udco.ordered_product_item_id = opi.id
                 AND udco.discount_code_setting_id IS NULL
                 AND dcs.first_digit = SUBSTRING(udco.code FROM 1 FOR 1)
                 AND dcs.following_2to4_digits = SUBSTRING(udco.code FROM 2 FOR 3)
                 AND dcs.deleted_at IS NULL
               ''')

    op.create_foreign_key('UsedDiscountCodeCart_ibfk_3', 'UsedDiscountCodeCart', 'DiscountCodeSetting',
                          ['discount_code_setting_id'], ['id'])
    op.create_foreign_key('UsedDiscountCodeOrder_ibfk_4', 'UsedDiscountCodeOrder', 'DiscountCodeSetting',
                          ['discount_code_setting_id'], ['id'])


def downgrade():
    op.drop_constraint('UsedDiscountCodeCart_ibfk_3', 'UsedDiscountCodeCart', type_='foreignkey')
    op.drop_constraint('UsedDiscountCodeOrder_ibfk_4', 'UsedDiscountCodeOrder', type_='foreignkey')
    # Those below methods are for development purpose.
    #
    # op.execute('''
    #            UPDATE `UsedDiscountCodeCart` udcc
    #            SET udcc.applied_amount = NULL,
    #                udcc.discount_code_setting_id = NULL,
    #                udcc.benefit_amount = NULL,
    #                udcc.benefit_unit = NULL
    #            ''')
    #
    # op.execute('''
    #            UPDATE `UsedDiscountCodeOrder` udco
    #            SET udco.applied_amount = NULL,
    #                udco.discount_code_setting_id = NULL,
    #                udco.benefit_amount = NULL,
    #                udco.benefit_unit = NULL
    #            ''')
