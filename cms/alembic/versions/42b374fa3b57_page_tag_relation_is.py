"""page tag relation is changed

Revision ID: 42b374fa3b57
Revises: f200bd70712
Create Date: 2013-02-20 16:36:59.581115

"""

# revision identifiers, used by Alembic.
revision = '42b374fa3b57'
down_revision = 'f200bd70712'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    print "==========--warnigs--============="
    print "page <-> tag relation is deleted"
    op.execute("delete from pagetag2page;")
    op.drop_constraint("fk_pagetag2page_object_id_to_page_id", "pagetag2page", type="foreignkey")
    op.drop_index("fk_pagetag2page_object_id_to_page_id", "pagetag2page") #innnodb
    op.create_foreign_key("fk_pagetag2page_object_id_to_page_id", "pagetag2page", "pagesets", ["object_id"], ["id"])

def downgrade():
    op.drop_constraint("fk_pagetag2page_object_id_to_page_id", "pagetag2page", type="foreignkey")
    op.drop_index("fk_pagetag2page_object_id_to_page_id", "pagetag2page") #innnodb
    op.create_foreign_key("fk_pagetag2page_object_id_to_page_id", "pagetag2page", "page", ["object_id"], ["id"])
