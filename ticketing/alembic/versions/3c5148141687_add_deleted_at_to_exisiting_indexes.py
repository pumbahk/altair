"""add deleted_at to exisiting indexes

Revision ID: 3c5148141687
Revises: 26aa199ca459
Create Date: 2015-04-16 12:07:06.449407

"""

# revision identifiers, used by Alembic.
revision = '3c5148141687'
down_revision = '26aa199ca459'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    # https://redmine.ticketstar.jp/issues/10870
    op.execute("""
ALTER TABLE `ticketing`.`UserCredential` DROP INDEX `membership_id`, ADD INDEX `ix_membership_id_deleted_at` (`membership_id`, `deleted_at`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`Member` DROP INDEX `Member_ibfk_2`, ADD INDEX `ix_user_id_deleted_at` (`user_id`, `deleted_at`);
    """)

def downgrade():
    op.execute("""
ALTER TABLE `ticketing`.`UserCredential` DROP INDEX `ix_membership_id_deleted_at`, ADD INDEX `membership_id` (`membership_id`);
    """)
    op.execute("""
ALTER TABLE `ticketing`.`Member` DROP INDEX `ix_user_id_deleted_at`, ADD INDEX `Member_ibfk_2` (`user_id`);
    """)
