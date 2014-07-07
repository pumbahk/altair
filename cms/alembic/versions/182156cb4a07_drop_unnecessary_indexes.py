"""drop_unnecessary_indexes

Revision ID: 182156cb4a07
Revises: 4014a4a8f80e
Create Date: 2014-07-07 01:28:15.404683

"""

# revision identifiers, used by Alembic.
revision = '182156cb4a07'
down_revision = '4014a4a8f80e'

from alembic import op
import sqlalchemy as sa


def upgrade():
    # https://redmine.ticketstar.jp/issues/8877#note-19
    op.execute("""
ALTER TABLE `altaircms`.`genre_path` DROP INDEX `genre_id`;
    """)
    op.execute("""
ALTER TABLE `altaircms`.`host` DROP INDEX `ix_host_host_name`;
    """)
    op.execute("""
ALTER TABLE `altaircms`.`pagesets` DROP INDEX `pagesets_organization_idx`;
    """)


def downgrade():
    # do nothing here because it might cause severe service outage
    pass
