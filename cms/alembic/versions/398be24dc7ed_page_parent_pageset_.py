"""page.parent -> pageset.parent

Revision ID: 398be24dc7ed
Revises: 2e08e4e22fe6
Create Date: 2012-04-25 11:36:19.174159

"""

# revision identifiers, used by Alembic.
revision = '398be24dc7ed'
down_revision = '2e08e4e22fe6'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.execute("ALTER TABLE page DROP FOREIGN KEY fk_page_parent_id")
    op.drop_column("page", "parent_id")
    op.add_column("pagesets",
                  sa.Column("parent_id", sa.INTEGER, sa.ForeignKey("pagesets.id", name="fk_pagesets_parent_id")))


def downgrade():
    op.execute("ALTER TABLE pagesets DROP FOREIGN KEY fk_pagesets_parent_id")
    op.drop_column("pagesets", "parent_id")
    op.add_column("page", 
                  sa.Column("parent_id", sa.INTEGER, sa.ForeignKey("page.parent_id")))
    op.create_foreign_key("fk_page_parent_id", "page", "page", ["parent_id"], ["id"])

