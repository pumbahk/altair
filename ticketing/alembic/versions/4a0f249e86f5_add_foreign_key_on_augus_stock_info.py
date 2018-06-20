"""add_foreign_key_on_augus_stock_info

Revision ID: 4a0f249e86f5
Revises: 46e7a3beea4a
Create Date: 2018-06-19 14:34:05.549721

"""

# revision identifiers, used by Alembic.
revision = '4a0f249e86f5'
down_revision = '46e7a3beea4a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusStockInfo_ibfk_1',
        source='AugusStockInfo',
        referent='AugusPerformance',
        local_cols=['augus_performance_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusStockInfo_ibfk_2',
        source='AugusStockInfo',
        referent='AugusTicket',
        local_cols=['augus_ticket_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusStockInfo_ibfk_3',
        source='AugusStockInfo',
        referent='AugusAccount',
        local_cols=['augus_account_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusStockInfo_ibfk_4',
        source='AugusStockInfo',
        referent='Seat',
        local_cols=['seat_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint('AugusStockInfo_ibfk_1', 'AugusStockInfo', type_='foreignkey')
    op.drop_constraint('AugusStockInfo_ibfk_2', 'AugusStockInfo', type_='foreignkey')
    op.drop_constraint('AugusStockInfo_ibfk_3', 'AugusStockInfo', type_='foreignkey')
    op.drop_constraint('AugusStockInfo_ibfk_4', 'AugusStockInfo', type_='foreignkey')
    op.drop_index('AugusStockInfo_ibfk_1', 'AugusStockInfo')
    op.drop_index('AugusStockInfo_ibfk_2', 'AugusStockInfo')
    op.drop_index('AugusStockInfo_ibfk_3', 'AugusStockInfo')
    op.drop_index('AugusStockInfo_ibfk_4', 'AugusStockInfo')
