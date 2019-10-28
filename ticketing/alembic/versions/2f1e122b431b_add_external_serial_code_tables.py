"""add external serial code tables

Revision ID: 2f1e122b431b
Revises: 3b25f0dfa9a2
Create Date: 2019-10-28 14:08:07.699146

"""

# revision identifiers, used by Alembic.
revision = '2f1e122b431b'
down_revision = '3b25f0dfa9a2'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table(
        'ExternalSerialCodeSetting',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('product_item_id', Identifier, nullable=False, index=True),
        sa.Column('label', sa.String(length=255), nullable=True, default=""),
        sa.Column('description', sa.TEXT(), nullable=True, default=""),
        sa.Column('start_at', sa.DATETIME(), nullable=False, index=True),
        sa.Column('end_at', sa.DATETIME(), nullable=True, index=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['product_item_id'], ['ProductItem.id'], name="ExternalSerialCodeSetting_ibfk_1")
    )
    op.create_table(
        'ExternalSerialCode',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('external_serial_code_setting_id', Identifier, nullable=False, index=True),
        sa.Column('code_1_name', sa.String(length=255), nullable=True, default=""),
        sa.Column('code_1', sa.String(length=255), nullable=True, default=""),
        sa.Column('code_2_name', sa.String(length=255), nullable=True, default=""),
        sa.Column('code_2', sa.String(length=255), nullable=True, default=""),
        sa.Column('used_at', sa.DATETIME(), nullable=True, index=True, default=None),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['external_serial_code_setting_id'], ['ExternalSerialCodeSetting.id'], name="ExternalSerialCode_ibfk_1"),
    )
    op.create_table(
        'ExternalSerialCodeOrder',
        sa.Column('id', Identifier, primary_key=True),
        sa.Column('external_serial_code_id', Identifier, nullable=False, index=True),
        sa.Column('ordered_product_item_token_id', Identifier, nullable=False, index=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
        sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
        sa.ForeignKeyConstraint(['external_serial_code_id'], ['ExternalSerialCode.id'], name="ExternalSerialCodeOrder_ibfk_1"),
        sa.ForeignKeyConstraint(['ordered_product_item_token_id'], ['OrderedProductItemToken.id'], name="ExternalSerialCodeOrder_ibfk_2"),
    )


def downgrade():
    op.drop_table('ExternalSerialCodeOrder')
    op.drop_table('ExternalSerialCode')
    op.drop_table('ExternalSerialCodeSetting')


