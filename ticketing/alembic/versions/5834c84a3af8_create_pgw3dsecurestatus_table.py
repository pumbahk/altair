"""create_PGW3DSecureStatus_table

Revision ID: 5834c84a3af8
Revises: 54ed57d1575b
Create Date: 2019-06-18 18:48:39.792811

"""

# revision identifiers, used by Alembic.
revision = '5834c84a3af8'
down_revision = '54ed57d1575b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PGW3DSecureStatus',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('pgw_sub_service_id', sa.Unicode(length=50), nullable=False),
                    sa.Column('payment_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('enrollment_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('agency_request_id', sa.Unicode(length=255), nullable=False),
                    sa.Column('three_d_auth_status', sa.Unicode(length=100), nullable=False),
                    sa.Column('cavv_algorithm', sa.SmallInteger, nullable=True),
                    sa.Column('cavv', sa.Unicode(length=40), nullable=True),
                    sa.Column('eci', sa.Unicode(length=2), nullable=True),
                    sa.Column('transaction_id', sa.Unicode(length=40), nullable=True),
                    sa.Column('transaction_status', sa.Unicode(length=1), nullable=True),
                    sa.Column('three_d_internal_status', sa.SmallInteger, nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(),
                              server_default=sqlf.current_timestamp(), index=True, nullable=False),
                    sa.Column('updated_at', sa.TIMESTAMP(), server_default=text('0'), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('payment_id', name="ix_PGW3DSecureStatus_payment_id"),
                    sa.UniqueConstraint('enrollment_id', name="ix_PGW3DSecureStatus_enrollment_id")
                    )


def downgrade():
    op.drop_table('PGW3DSecureStatus')
