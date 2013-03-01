# -*- coding:utf-8 -*-
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

def oldupgrade():
    print "==========--warnigs--============="
    print "page <-> tag relation is deleted"
    op.execute("delete from pagetag2page;")
    op.drop_constraint("fk_pagetag2page_object_id_to_page_id", "pagetag2page", type="foreignkey")
    op.drop_index("fk_pagetag2page_object_id_to_page_id", "pagetag2page") #innnodb
    op.create_foreign_key("fk_pagetag2page_object_id_to_page_id", "pagetag2page", "pagesets", ["object_id"], ["id"])

### pagetag2pageではなくpagetag2pagesetを使う
def upgrade():
    op.create_table('pagetag2pageset',
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['pagesets.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['pagetag.id'], ),
                    sa.PrimaryKeyConstraint('object_id', "tag_id")
                    )

    ## data migration
    op.execute('insert into pagetag2pageset (object_id, tag_id) select p.pageset_id as object_id, x.tag_id as tag_id from pagetag2page as x join page as p on x.object_id = p.id group by p.pageset_id;')
    
def downgrade():
    op.drop_table("pagetag2pageset")


def old_downgrade():
    op.drop_constraint("fk_pagetag2page_object_id_to_page_id", "pagetag2page", type="foreignkey")
    op.drop_index("fk_pagetag2page_object_id_to_page_id", "pagetag2page") #innnodb
    op.create_foreign_key("fk_pagetag2page_object_id_to_page_id", "pagetag2page", "page", ["object_id"], ["id"])
