"""drop_unnecessary_indexes

Revision ID: 48b361955fed
Revises: 12b52292a9c0
Create Date: 2014-07-07 00:58:17.392029

"""

# revision identifiers, used by Alembic.
revision = '48b361955fed'
down_revision = '12b52292a9c0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://redmine.ticketstar.jp/issues/8877#note-19
    op.execute("""
ALTER TABLE `ticketing`.`CartedProductItem_Seat` DROP INDEX `carted_product_item_id`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`CheckinTokenReservation` DROP INDEX `ix_token_id_deleted_at`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`MailSubscription` DROP INDEX `email`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`Seat` DROP INDEX `ik_row_l0_id`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`SejOrder` DROP INDEX `ix_SejOrder_order_no`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`Venue` DROP FOREIGN KEY `Venue_ibfk_2`;
    """)

def downgrade():
    # do nothing here because it might cause severe service outage
    pass
