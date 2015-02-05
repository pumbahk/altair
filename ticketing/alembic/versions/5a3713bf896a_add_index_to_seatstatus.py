"""add index to SeatStatus

Revision ID: 5a3713bf896a
Revises: 482f7ef338d1
Create Date: 2015-02-04 00:43:43.631491

"""

# revision identifiers, used by Alembic.
revision = '5a3713bf896a'
down_revision = '482f7ef338d1'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://redmine.ticketstar.jp/issues/10799
    op.execute("""
ALTER TABLE `ticketing`.`SeatStatus` ADD INDEX `ix_status_updated_at` (`status`,`updated_at`);
    """)

def downgrade():
    op.execute("""
ALTER TABLE `ticketing`.`SeatStatus` DROP INDEX `ix_status_updated_at`;
    """)
