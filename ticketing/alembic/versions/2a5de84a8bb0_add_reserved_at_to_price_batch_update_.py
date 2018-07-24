"""add reserved_at to price_batch_update_task

Revision ID: 2a5de84a8bb0
Revises: 51e1d0bf8628
Create Date: 2018-07-17 14:39:03.443208

"""

# revision identifiers, used by Alembic.
revision = '2a5de84a8bb0'
down_revision = '51e1d0bf8628'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(u'PriceBatchUpdateTask', sa.Column('reserverd_at', sa.TIMESTAMP(), nullable=False))

def downgrade():
    op.drop_column(u'PriceBatchUpdateTask', 'reserverd_at')