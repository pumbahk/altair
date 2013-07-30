"""static page unique constraint is url-organization_id-pagetype_id

Revision ID: 143da9f95f13
Revises: 143c45be235a
Create Date: 2013-07-30 19:41:09.056667

"""

# revision identifiers, used by Alembic.
revision = '143da9f95f13'
down_revision = '143c45be235a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_constraint("url", "static_pagesets", type="unique")
    op.create_unique_constraint("url", "static_pagesets", ["url", "organization_id", "pagetype_id"])

def downgrade():
    op.drop_constraint("url", "static_pagesets", type="unique")
    op.create_unique_constraint("url", "static_pagesets", ["url", "organization_id"])
