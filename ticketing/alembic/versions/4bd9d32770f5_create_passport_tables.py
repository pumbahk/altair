# -*- coding:utf-8 -*-
"""create passport tables

Revision ID: 4bd9d32770f5
Revises: 414f5d7e22cc
Create Date: 2018-06-13 15:20:00.066822

"""

# revision identifiers, used by Alembic.
revision = '4bd9d32770f5'
down_revision = '414f5d7e22cc'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # パスポート販売を有効にするフラグ
    op.add_column(u'OrganizationSetting', sa.Column("enable_passport", sa.Boolean(), server_default=('0')))

    # パスポートテーブル
    op.create_table('Passport',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('name', sa.String(length=1024), nullable=True),
        sa.Column('available_day', Identifier(), nullable=True),
        sa.Column('daily_passport', sa.Boolean(), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('organization_id', Identifier(), nullable=True),
        sa.Column('performance_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], 'Passport_ibfk_1'),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], 'Passport_ibfk_2'),
        sa.PrimaryKeyConstraint('id')
        )

    # パスポート入場不可期間テーブル
    op.create_table('PassportNotAvailableTerm',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('start_on', sa.TIMESTAMP(), nullable=True),
        sa.Column('end_on', sa.TIMESTAMP(), nullable=True),
        sa.Column('passport_id', Identifier(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['passport_id'], ['Passport.id'], 'PassportNotAvailable_ibfk_1'),
        sa.PrimaryKeyConstraint('id')
        )

    # パスポート購入者テーブル
    op.create_table('PassportUser',
        sa.Column('id', Identifier(), nullable=False),
        sa.Column('order_id', Identifier(), nullable=True),
        sa.Column('ordered_product_id', Identifier(), nullable=True),
        sa.Column('order_attribute_num', Identifier(), nullable=True),
        sa.Column('expired_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('image_path', sa.String(length=1024), nullable=True),
        sa.Column('is_valid', sa.Boolean(), nullable=True),
        sa.Column('passport_id', Identifier(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['passport_id'], ['Passport.id'], 'PassportUser_ibfk_1'),
        sa.ForeignKeyConstraint(['order_id'], ['Order.id'], 'PassportUser_ibfk_2'),
        sa.ForeignKeyConstraint(['ordered_product_id'], ['OrderedProduct.id'], 'PassportUser_ibfk_3'),
        sa.PrimaryKeyConstraint('id')
        )


def downgrade():
    op.drop_table('PassportUser')
    op.drop_table('PassportNotAvailableTerm')
    op.drop_table('Passport')
    op.drop_column(u'OrganizationSetting', "enable_passport")
