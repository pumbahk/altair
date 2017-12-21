# encoding: utf-8

"""Add Enable Discount Code To Organization Setting

Revision ID: 4cef5d7f0122
Revises: 1ae90f027aba
Create Date: 2017-11-16 17:00:44.911030

"""

# revision identifiers, used by Alembic.
revision = '4cef5d7f0122'
down_revision = '1ae90f027aba'

import sqlalchemy as sa
from alembic import op
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.sql.expression import text

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_discount_code', sa.Boolean, server_default=text('0'), nullable=False))

    # イーグルスのみクーポン・割引コード設定をデフォルトでONにしておく
    sql = """\
        UPDATE OrganizationSetting 
        SET enable_discount_code = 1 
        WHERE organization_id = 24
    """
    op.execute(sql)

    op.create_table(
        'DiscountCodeSetting',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('is_valid', sa.Boolean, server_default=text('0'), nullable=False),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('issued_by', sa.Unicode(255), nullable=False),
        sa.Column('first_digit', sa.Unicode(1), nullable=True),
        sa.Column('following_2to4_digits', sa.Unicode(3), nullable=True),
        sa.Column('criterion', sa.Unicode(255), nullable=False),
        sa.Column('condition_price_amount', sa.Unicode(255), nullable=True),
        sa.Column('condition_price_more_or_less', sa.Unicode(255), nullable=True),
        sa.Column('benefit_amount', sa.Integer(8), nullable=False),
        sa.Column('benefit_unit', sa.Unicode(1), nullable=False),
        sa.Column('start_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('end_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('explanation', sa.UnicodeText, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="DiscountCodeSetting_ibfk_1"),
    )

    op.create_table(
        'DiscountCode',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_setting_id', Identifier, nullable=False),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('operator_id', Identifier, nullable=False),
        sa.Column('code', sa.Unicode(12), nullable=False, index=True),
        sa.Column('order_no', sa.Unicode(255), nullable=True, index=True),
        sa.Column('used_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_setting_id'], ['DiscountCodeSetting.id'], ondelete="CASCADE",
                                name="DiscountCode_ibfk_1"),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="DiscountCode_ibfk_2"),
        sa.ForeignKeyConstraint(['operator_id'], ['Operator.id'], name="DiscountCode_ibfk_3"),
        sa.UniqueConstraint('organization_id', 'code', name='organization_code'),
    )

    op.create_table(
        'DiscountCodeTarget',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_setting_id', Identifier, nullable=False),
        sa.Column('event_id', Identifier, nullable=True),
        sa.Column('performance_id', Identifier, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_setting_id'], ['DiscountCodeSetting.id'],
                                name="DiscountCodeTarget_ibfk_1"),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], name="DiscountCodeTarget_ibfk_2"),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="DiscountCodeTarget_ibfk_3"),
        sa.UniqueConstraint('discount_code_setting_id', 'event_id', 'performance_id', 'created_at',
                            name='unique_target'),
    )


def downgrade():
    op.drop_table('DiscountCode')
    op.drop_table('DiscountCodeTarget')
    op.drop_table('DiscountCodeSetting')
    op.drop_column('OrganizationSetting', u'enable_discount_code')
