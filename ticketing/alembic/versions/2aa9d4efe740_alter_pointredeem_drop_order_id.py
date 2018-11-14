"""Alter PointRedeem DROP order_id

Revision ID: 2aa9d4efe740
Revises: 31b7c716d9bb
Create Date: 2018-11-14 20:55:45.154145

"""

# revision identifiers, used by Alembic.
revision = '2aa9d4efe740'
down_revision = '31b7c716d9bb'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.drop_column('PointRedeem', 'order_id')

def downgrade():
    op.execute('ALTER TABLE PointRedeem ADD COLUMN `order_id` bigint(20) NOT NULL AFTER `unique_id`')
    op.create_unique_constraint('ix_PointRedeem_order_id', 'PointRedeem', ['order_id'])
