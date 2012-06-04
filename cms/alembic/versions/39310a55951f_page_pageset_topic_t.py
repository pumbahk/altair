"""page->pageset topic,topcontent

Revision ID: 39310a55951f
Revises: 52602e18e0ff
Create Date: 2012-05-28 19:52:49.621370

"""

# revision identifiers, used by Alembic.
revision = '39310a55951f'
down_revision = '52602e18e0ff'

from alembic import op
import sqlalchemy as sa

## todo: fix
def upgrade():
    op.add_column('topic', sa.Column('linked_page_id', sa.Integer(), sa.ForeignKey("pagesets.id", use_alter=True, name="topic_ibfk_5"), nullable=True))
    op.add_column('topic', sa.Column('bound_page_id', sa.Integer(), sa.ForeignKey("pagesets.id", use_alter=True, name="topic_ibfk_6"),nullable=True))

    op.execute("alter table topic add constraint topic_ibfk_5 foreign key (linked_page_id) references pagesets(id);")
    op.execute("alter table topic add constraint topic_ibfk_6 foreign key (bound_page_id) references pagesets(id);")

    op.execute("ALTER TABLE topic DROP FOREIGN KEY topic_ibfk_3")
    op.drop_column('topic', u'page_id')

    ## topcontent
    op.add_column('topcontent', sa.Column('linked_page_id', sa.Integer(), sa.ForeignKey("pagesets.id", use_alter=True, name="topcontent_ibfk_5"), nullable=True))
    op.add_column('topcontent', sa.Column('bound_page_id', sa.Integer(), sa.ForeignKey("pagesets.id", use_alter=True, name="topcontent_ibfk_6"),nullable=True))

    op.execute("alter table topcontent add constraint topcontent_ibfk_5 foreign key (linked_page_id) references pagesets(id);")
    op.execute("alter table topcontent add constraint topcontent_ibfk_6 foreign key (bound_page_id) references pagesets(id);")

    op.execute("ALTER TABLE topcontent DROP FOREIGN KEY topcontent_ibfk_3")
    op.drop_column('topcontent', u'page_id')

def downgrade():
    op.add_column('topic', sa.Column(u'page_id', sa.Integer(), sa.ForeignKey("page.id", use_alter=True, name="topic_ibfk_3"), nullable=True))
    op.execute("alter table topic add constraint topic_ibfk_3 foreign key (page_id) references page(id);")

    op.execute("ALTER TABLE topic DROP FOREIGN KEY topic_ibfk_5")
    op.execute("ALTER TABLE topic DROP FOREIGN KEY topic_ibfk_6")
    op.drop_column('topic', 'bound_page_id')
    op.drop_column('topic', 'linked_page_id')

    ## topcontent
    op.add_column('topcontent', sa.Column(u'page_id', sa.Integer(), sa.ForeignKey("page.id", use_alter=True, name="topcontent_ibfk_3"), nullable=True))
    op.execute("alter table topcontent add constraint topcontent_ibfk_3 foreign key (page_id) references page(id);")

    op.execute("ALTER TABLE topcontent DROP FOREIGN KEY topcontent_ibfk_5")
    op.execute("ALTER TABLE topcontent DROP FOREIGN KEY topcontent_ibfk_6")
    op.drop_column('topcontent', 'bound_page_id')
    op.drop_column('topcontent', 'linked_page_id')

