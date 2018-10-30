"""create_pointredeem_table

Revision ID: 573acbd34f51
Revises: 2ca5bcfe9618
Create Date: 2018-10-26 13:58:14.406200

"""

# revision identifiers, used by Alembic.
revision = '573acbd34f51'
down_revision = '2ca5bcfe9618'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_table('PointRedeem',
                    sa.Column('id', Identifier(), nullable=False),
                    sa.Column('easy_id', sa.Unicode(length=16), index=True, nullable=False),
                    sa.Column('unique_id', Identifier(), nullable=False),
                    sa.Column('order_id', Identifier(), nullable=False),
                    sa.Column('order_no', sa.Unicode(length=255), nullable=False),
                    sa.Column('group_id', sa.Integer(), nullable=False),
                    sa.Column('reason_id', sa.Integer(), nullable=False),
                    sa.Column('point_status', sa.Integer(), index=True, nullable=False),
                    sa.Column('auth_point', sa.Integer(), nullable=False),
                    sa.Column('authed_at', sa.TIMESTAMP(), index=True, nullable=True),
                    sa.Column('fix_point', sa.Integer(), nullable=True),
                    sa.Column('fixed_at', sa.TIMESTAMP(), index=True, nullable=True),
                    sa.Column('canceled_at', sa.TIMESTAMP(), index=True, nullable=True),
                    sa.Column('created_at', sa.TIMESTAMP(), server_default=sqlf.current_timestamp(), nullable=False),
                    sa.Column('deleted_at', sa.TIMESTAMP(), nullable=True),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('unique_id', name="ix_PointRedeem_unique_id"),
                    sa.UniqueConstraint('order_id', name="ix_PointRedeem_order_id"),
                    sa.UniqueConstraint('order_no', name="ix_PointRedeem_order_no")
                    )


def downgrade():
    op.drop_table('PointRedeem')
