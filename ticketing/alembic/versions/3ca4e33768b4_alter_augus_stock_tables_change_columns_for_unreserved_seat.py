"""Alter table AugusStockInfo and AugusStockDetail change columns for unreserved seat

Revision ID: 3ca4e33768b4
Revises: 1d6f11b5d485
Create Date: 2018-08-21 15:49:51.300156

"""

# revision identifiers, used by Alembic.
revision = '3ca4e33768b4'
down_revision = '1d6f11b5d485'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger
INVALIDATE_AUGUS_SEAT_ID = -1

def upgrade():
    op.alter_column('AugusStockInfo', 'augus_seat_id', existing_type=Identifier, nullable=True)
    op.execute("UPDATE AugusStockInfo SET augus_seat_id = NULL WHERE augus_seat_id = {}"
               .format(INVALIDATE_AUGUS_SEAT_ID))
    op.add_column('AugusStockDetail',
                  sa.Column('augus_unreserved_putback_status', sa.Integer(), nullable=True))


def downgrade():
    op.execute("UPDATE AugusStockInfo SET augus_seat_id = {} WHERE augus_seat_id IS NULL"
               .format(INVALIDATE_AUGUS_SEAT_ID))
    op.alter_column('AugusStockInfo', 'augus_seat_id', existing_type=Identifier, nullable=False)
    op.drop_column('AugusStockDetail', 'augus_unreserved_putback_status')
