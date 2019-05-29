"""create_pgworderstatus_table

Revision ID: 402f797572f4
Revises: 25fdb9f6af4f
Create Date: 2019-05-28 16:42:04.752858

"""

# revision identifiers, used by Alembic.
revision = '402f797572f4'
down_revision = '25fdb9f6af4f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf
from sqlalchemy.dialects.mysql import TINYINT

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PGWOrderStatus',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('pgw_sub_service_id', sa.Unicode(length=50), nullable=True),
                    sa.Column('payment_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('card_token', sa.Unicode(length=50), nullable=False),
                    sa.Column('cvv_token', sa.Unicode(length=50), nullable=False),
                    sa.Column('enrolled_at', sa.DateTime(), index=True, nullable=True),
                    sa.Column('authed_at', sa.DateTime(), index=True, nullable=True),
                    sa.Column('captured_at', sa.DateTime(), index=True, nullable=True),
                    sa.Column('canceled_at', sa.DateTime(), index=True, nullable=True),
                    sa.Column('refunded_at', sa.DateTime(), index=True, nullable=True),
                    sa.Column('payment_status', sa.SmallInteger, index=True, nullable=False),
                    sa.Column('gross_amount', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.TIMESTAMP(),
                              server_default=sqlf.current_timestamp(), index=True, nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('payment_id', name="ix_PGWOrderStatus_payment_id")
                    )


def downgrade():
    op.drop_table('PGWOrderStatus')
