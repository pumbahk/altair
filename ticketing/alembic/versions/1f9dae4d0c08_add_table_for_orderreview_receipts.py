"""add table for orderreview receipts

Revision ID: 1f9dae4d0c08
Revises: 31be005d05e9
Create Date: 2017-08-07 14:03:38.532123

"""

# revision identifiers, used by Alembic.
revision = '1f9dae4d0c08'
down_revision = '31be005d05e9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('OrderReceipt',
                    sa.Column('id', Identifier, nullable=False),
                    sa.Column('order_id', Identifier(), nullable=True),
                    sa.Column('issued_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], 'OrderReceipt_ibfk_1'),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_index('OrderReceipt_ibfk_2', 'OrderReceipt', ['order_id'])
def downgrade():
    op.drop_index('OrderReceipt_ibfk_2', 'OrderReceipt')
    op.drop_table('OrderReceipt')
