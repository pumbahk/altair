"""add resale tables

Revision ID: 430e25d95def
Revises: 41e3c7e113c0
Create Date: 2018-03-19 16:49:57.109438

"""

# revision identifiers, used by Alembic.
revision = '430e25d95def'
down_revision = '41e3c7e113c0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('ResaleSegment',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('start_at', sa.DateTime(), nullable=False),
                    sa.Column('end_at', sa.DateTime(), nullable=False),
                    sa.Column('performance_id', Identifier(), nullable=False, index=True),
                    sa.Column('sent_at', sa.TIMESTAMP(), nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.create_table('ResaleRequest',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('resale_segment_id', Identifier(), nullable=False, index=True),
                    sa.Column('ordered_product_item_token_id', Identifier(), nullable=False),
                    sa.Column('bank_code', sa.Unicode(32), nullable=False),
                    sa.Column('bank_branch_code', sa.Unicode(32), nullable=False),
                    sa.Column('account_number', sa.Unicode(32), nullable=False),
                    sa.Column('account_holder_name', sa.Unicode(255), nullable=False),
                    sa.Column('total_amount', sa.Numeric(precision=16, scale=2), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['resale_segment_id'], ['ResaleSegment.id'], 'ResaleRequest_ibfk_1'),
                    sa.PrimaryKeyConstraint('id')
                    )


def downgrade():
    op.drop_table('ResaleRequest')
    op.drop_table('ResaleSegment')

