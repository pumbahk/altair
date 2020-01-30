"""drop_index_TicketHubItems_table

Revision ID: 1d494fd22d5b
Revises: 301d140b11b9
Create Date: 2020-01-30 15:06:29.561637

"""

# revision identifiers, used by Alembic.
revision = '1d494fd22d5b'
down_revision = '301d140b11b9'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute("""
ALTER TABLE `ticketing`.`TicketHubItemGroup` DROP INDEX `code`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`TicketHubItem` DROP INDEX `code`;
    """)


def downgrade():
    op.execute("""
ALTER TABLE `ticketing`.`TicketHubItemGroup` ADD INDEX `code`;
    """)
    op.execute("""
ALTER TABLE `ticketing`.`TicketHubItem` ADD INDEX `code`;
    """)
