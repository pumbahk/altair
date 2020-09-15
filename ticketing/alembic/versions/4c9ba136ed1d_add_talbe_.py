"""add talbe ExternalSerialCodeProductItemPair

Revision ID: 4c9ba136ed1d
Revises: 273f3bd41ee7
Create Date: 2020-09-03 11:40:58.191348

"""

# revision identifiers, used by Alembic.
revision = '4c9ba136ed1d'
down_revision = '273f3bd41ee7'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():

    op.create_table('ExternalSerialCodeProductItemPair',
                    sa.Column('id', Identifier(), primary_key=True),
                    sa.Column('external_serial_code_setting_id', Identifier(), nullable=False),
                    sa.Column('product_item_id', Identifier(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.ForeignKeyConstraint(['external_serial_code_setting_id'], ['ExternalSerialCodeSetting.id'],
                                            'ExternalSerialCodeProductItemPair_ibfk_1', ondelete='cascade'),
                    sa.ForeignKeyConstraint(['product_item_id'], ['ProductItem.id'],
                                            'ExternalSerialCodeProductItemPair_ibfk_2', ondelete='cascade'),
                    )


def downgrade():
    op.drop_table('ExternalSerialCodeProductItemPair')

