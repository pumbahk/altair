"""add_foreign_key_on_augus_stock_detail

Revision ID: 46e7a3beea4a
Revises: 43d285326a6d
Create Date: 2018-06-19 14:33:58.860006

"""

# revision identifiers, used by Alembic.
revision = '46e7a3beea4a'
down_revision = '43d285326a6d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.create_foreign_key(
        name='AugusStockDetail_ibfk_1',
        source='AugusStockDetail',
        referent='AugusStockInfo',
        local_cols=['augus_stock_info_id'],
        remote_cols=['id'],
        onupdate='CASCADE',
        ondelete='CASCADE'
    )

    op.create_foreign_key(
        name='AugusStockDetail_ibfk_2',
        source='AugusStockDetail',
        referent='AugusPutback',
        local_cols=['augus_putback_id'],
        remote_cols=['id']
    )

    op.create_foreign_key(
        name='AugusStockDetail_ibfk_3',
        source='AugusStockDetail',
        referent='AugusTicket',
        local_cols=['augus_ticket_id'],
        remote_cols=['id']
    )


def downgrade():
    op.drop_constraint('AugusStockDetail_ibfk_1', 'AugusStockDetail', type_='foreignkey')
    op.drop_constraint('AugusStockDetail_ibfk_2', 'AugusStockDetail', type_='foreignkey')
    op.drop_constraint('AugusStockDetail_ibfk_3', 'AugusStockDetail', type_='foreignkey')
    op.drop_index('AugusStockDetail_ibfk_1', 'AugusStockDetail')
    op.drop_index('AugusStockDetail_ibfk_2', 'AugusStockDetail')
    op.drop_index('AugusStockDetail_ibfk_3', 'AugusStockDetail')
