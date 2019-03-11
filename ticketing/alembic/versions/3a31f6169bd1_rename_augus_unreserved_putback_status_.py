"""Rename augus_unreserved_putback_status column at AugusStockDetail

Revision ID: 3a31f6169bd1
Revises: 16d8ed4fdf59
Create Date: 2019-02-26 10:09:44.215912

"""

# revision identifiers, used by Alembic.
revision = '3a31f6169bd1'
down_revision = '16d8ed4fdf59'

from alembic import op


def upgrade():
    op.execute('ALTER TABLE AugusStockDetail CHANGE COLUMN augus_unreserved_putback_status' +
               ' augus_scheduled_putback_status int(11) DEFAULT NULL')


def downgrade():
    op.execute('ALTER TABLE AugusStockDetail CHANGE COLUMN augus_scheduled_putback_status' +
               ' augus_unreserved_putback_status int(11) DEFAULT NULL')
