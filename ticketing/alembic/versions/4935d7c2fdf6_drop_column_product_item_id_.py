# -*- coding:utf-8 -*-
"""drop column product_item_id ExternalSerialCodeSetting

Revision ID: 4935d7c2fdf6
Revises: 2c98f57e91b2
Create Date: 2020-09-16 20:30:20.441890

"""

# revision identifiers, used by Alembic.
revision = '4935d7c2fdf6'
down_revision = '2c98f57e91b2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("ALTER TABLE `ExternalSerialCodeSetting` DROP FOREIGN KEY ExternalSerialCodeSetting_ibfk_1")
    op.execute("ALTER TABLE `ExternalSerialCodeSetting` DROP INDEX ix_ExternalSerialCodeSetting_product_item_id;")
    op.drop_column('ExternalSerialCodeSetting', 'product_item_id')


def downgrade():
    # NullがFalseなので、もう外部キーは入れれない。そのため、upgradeの１行目は実行できなくなる。
    op.add_column('ExternalSerialCodeSetting',
                  sa.Column('product_item_id', Identifier, nullable=False))
    op.execute("""
ALTER TABLE `ticketing`.`ExternalSerialCodeSetting` ADD INDEX `ix_ExternalSerialCodeSetting_product_item_id` (`product_item_id`);
    """)
