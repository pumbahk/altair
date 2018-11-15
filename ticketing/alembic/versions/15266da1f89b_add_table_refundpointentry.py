"""add table RefundPointEntry

Revision ID: 15266da1f89b
Revises: 523e0f4cc800
Create Date: 2018-11-06 17:36:00.091858

"""

# revision identifiers, used by Alembic.
revision = '15266da1f89b'
down_revision = '523e0f4cc800'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('RefundPointEntry',
                    sa.Column('id', Identifier, nullable=False),
                    sa.Column('order_id', Identifier(), nullable=False),
                    sa.Column('order_no', sa.Unicode(length=255), nullable=False),
                    sa.Column('refund_point_amount', sa.Numeric(precision=16, scale=2), nullable=False),
                    sa.Column('refunded_point_at', sa.DateTime(), nullable=True),
                    sa.Column('seq_no', sa.Integer(), nullable=False, default=1, server_default='1'),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.ForeignKeyConstraint(['order_id'], ['Order.id'], 'RefundPointEntry_ibfk_1'),
                    sa.PrimaryKeyConstraint('id'),
                    )

def downgrade():
    op.drop_table('RefundPointEntry')
