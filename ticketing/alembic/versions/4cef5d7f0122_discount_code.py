"""Add Enable Discount Code To Organization Setting

Revision ID: 4cef5d7f0122
Revises: 7d530c296b4
Create Date: 2017-11-16 17:00:44.911030

"""

# revision identifiers, used by Alembic.
revision = '4cef5d7f0122'
down_revision = '7d530c296b4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.add_column('OrganizationSetting',
                  sa.Column('enable_discount_code', sa.Boolean, server_default=text('0'), nullable=False))

    op.create_table(
        'DiscountCodeSetting',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('first_digit', sa.Unicode(1), nullable=False),
        sa.Column('following_2to4_digits', sa.Unicode(3), nullable=False),
        sa.Column('name', sa.Unicode(255), nullable=False),
        sa.Column('issued_by', sa.Unicode(255), nullable=False),
        sa.Column('criterion', sa.Unicode(255), nullable=False),
        sa.Column('condition', sa.Unicode(255), nullable=False),
        sa.Column('benefit_amount', sa.Integer(8), nullable=False),
        sa.Column('benefit_unit', sa.Unicode(1), nullable=False),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('is_valid', sa.Boolean, server_default=text('0'), nullable=False),
        sa.Column('valid_from', sa.TIMESTAMP(), nullable=True),
        sa.Column('valid_until', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="DiscountCodeSetting_ibfk_1"),
        sa.UniqueConstraint('organization_id', 'first_digit', 'following_2to4_digits', name='first_4_digits'),
    )

    op.create_table(
        'DiscountCode',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_setting_id', Identifier, nullable=False),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('code', sa.Unicode(12), nullable=False),
        sa.Column('order_no', sa.Unicode(255), nullable=True, index=True),
        sa.Column('used_at', sa.TIMESTAMP(), server_default=text('0'), nullable=True),
        sa.Column('created_by', sa.Unicode(255), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_setting_id'], ['DiscountCodeSetting.id'], name="DiscountCode_ibfk_1"),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="DiscountCode_ibfk_2"),
        sa.UniqueConstraint('organization_id', 'code', name='organization_code'),
    )

    op.create_table(
        'DiscountCodeTarget',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('discount_code_setting_id', Identifier, nullable=False),
        sa.Column('organization_id', Identifier, nullable=False),
        sa.Column('event_id', Identifier, nullable=False),
        sa.Column('performance_id', Identifier, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['discount_code_setting_id'], ['DiscountCodeSetting.id'], name="DiscountCodeTarget_ibfk_1"),
        sa.ForeignKeyConstraint(['organization_id'], ['Organization.id'], name="DiscountCodeTarget_ibfk_2"),
        sa.ForeignKeyConstraint(['event_id'], ['Event.id'], name="DiscountCodeTarget_ibfk_3"),
        sa.ForeignKeyConstraint(['performance_id'], ['Performance.id'], name="DiscountCodeTarget_ibfk_4"),
    )

def downgrade():
    op.drop_table('DiscountCode')
    op.drop_table('DiscountCodeTarget')
    op.drop_table('DiscountCodeSetting')
    op.drop_column('OrganizationSetting', u'enable_discount_code')
