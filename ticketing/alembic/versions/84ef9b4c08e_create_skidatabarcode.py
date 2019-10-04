"""Create SkidataBarcode.

Revision ID: 84ef9b4c08e
Revises: 332d68d3782c
Create Date: 2019-10-02 15:26:43.052405

"""

# revision identifiers, used by Alembic.
revision = '84ef9b4c08e'
down_revision = '332d68d3782c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('SkidataBarcode',
                    sa.Column('id', Identifier(), nullable=False, primary_key=True),
                    sa.Column('seat_id', Identifier(), nullable=True),
                    sa.Column('ordered_product_item_token_id', Identifier(), nullable=True),
                    sa.Column('data', sa.String(30), nullable=False),
                    sa.Column('error_code', sa.String(10), nullable=True),
                    sa.Column('sent_at', sa.DateTime(), nullable=True),
                    sa.Column('canceled_at', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['seat_id'], ['Seat.id'], 'SkidataBarcode_ibfk_1', ondelete='CASCADE'),
                    sa.ForeignKeyConstraint(['ordered_product_item_token_id'], ['OrderedProductItemToken.id'],
                                            'SkidataBarcode_ibfk_2', ondelete='CASCADE'),
                    sa.UniqueConstraint('data')
                    )


def downgrade():
    op.drop_table('SkidataBarcode')
