"""add_id_ticket_bundle_attribute

Revision ID: 10bf786de077
Revises: 3584d649de05
Create Date: 2012-08-16 18:35:27.841549

"""

# revision identifiers, used by Alembic.
revision = '10bf786de077'
down_revision = '3584d649de05'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE TicketBundleAttribute ADD COLUMN id bigint(20) NOT NULL;")
    op.execute("ALTER TABLE TicketBundleAttribute DROP PRIMARY KEY, ADD PRIMARY KEY (id);")
    op.execute("ALTER TABLE TicketBundleAttribute MODIFY COLUMN id bigint(20) NOT NULL AUTO_INCREMENT;")
    op.execute("ALTER TABLE TicketBundleAttribute ADD UNIQUE ib_unique_1 (ticket_bundle_id, name, deleted_at);")

def downgrade():
    op.execute("ALTER TABLE TicketBundleAttribute DROP INDEX ib_unique_1;")
    op.execute("ALTER TABLE TicketBundleAttribute MODIFY COLUMN id bigint(20) NOT NULL;")
    op.execute("ALTER TABLE TicketBundleAttribute DROP PRIMARY KEY, ADD PRIMARY KEY (ticket_bundle_id, name);")
    op.execute("ALTER TABLE TicketBundleAttribute DROP COLUMN id;")

