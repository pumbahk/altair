"""add index to RefundPointEntry

Revision ID: 4b041d4e9b85
Revises: 15266da1f89b
Create Date: 2018-11-08 14:48:19.499265

"""

# revision identifiers, used by Alembic.
revision = '4b041d4e9b85'
down_revision = '15266da1f89b'

from alembic import op
import sqlalchemy as sa

Identifier = sa.BigInteger


def upgrade():
    op.execute("""
    ALTER TABLE `ticketing`.`RefundPointEntry` ADD INDEX `RefundPointEntry_ibfk_2` (`order_no`);
        """)

def downgrade():
    op.execute("""
    ALTER TABLE `ticketing`.`RefundPointEntry` DROP INDEX `RefundPointEntry_ibfk_2`;
        """)
