"""augus_change

Revision ID: 2cda4724cc40
Revises: ee042788746
Create Date: 2014-02-14 17:33:14.725522

"""

# revision identifiers, used by Alembic.
revision = '2cda4724cc40'
down_revision = 'ee042788746'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.alter_column('AugusPerformance', 'performance_id', nullable=True,
                   name='performance_id', existing_type=Identifier, existing_nullable=False)
    op.alter_column('AugusPutback', 'reserverd_at', new_column_name='reserved_at',
                   existing_type=sa.TIMESTAMP())
    op.alter_column('AugusPutback', 'notificated_at', new_column_name='notified_at',
                   existing_type=sa.TIMESTAMP())
    op.add_column('AugusStockInfo', sa.Column('seat_id', Identifier(), nullable=True))


def downgrade():
    op.alter_column('AugusPerformance', 'performance_id', nullable=False,
                    name='performance_id', existing_type=Identifier, existing_nullable=True)
    op.alter_column('AugusPutback', 'reserved_at', new_column_name='reserverd_at',
                   existing_type=sa.TIMESTAMP())
    op.alter_column('AugusPutback', 'notified_at', new_column_name='notificated_at',
                   existing_type=sa.TIMESTAMP())
    op.drop_column('AugusStockInfo', 'seat_id')
