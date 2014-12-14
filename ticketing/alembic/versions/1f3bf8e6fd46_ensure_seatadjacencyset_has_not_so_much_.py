"""ensure SeatAdjacencySet has not so much entries; Seat should be pruned also by venue_id.

Revision ID: 1f3bf8e6fd46
Revises: a66f50feebd
Create Date: 2014-12-14 21:27:05.110799

"""

# revision identifiers, used by Alembic.
revision = '1f3bf8e6fd46'
down_revision = 'a66f50feebd'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://redmine.ticketstar.jp/issues/10454#note-3
    op.execute("""
ALTER TABLE `ticketing`.`SeatAdjacencySet` ADD INDEX `ix_adjacencies_at_most` (`site_id`,`seat_count`,`deleted_at`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`Seat` DROP INDEX `ix_Seat_l0_id`, ADD INDEX `ix_Seat_l0_id_venue_id` (`l0_id`,`venue_id`);
    """)

def downgrade():
    # do nothing here because it might cause severe service outage
    pass
