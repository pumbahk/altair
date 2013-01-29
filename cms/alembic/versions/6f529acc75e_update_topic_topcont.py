# -*- coding:utf-8 -*-
"""update topic topcontent

Revision ID: 6f529acc75e
Revises: 5a8a6eccba80
Create Date: 2013-01-29 16:07:57.604174

"""

# revision identifiers, used by Alembic.
revision = '6f529acc75e'
down_revision = '5a8a6eccba80'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


"""
warning:
今動いている89ersなどのcmsのデータはこのmigrationを実行すると消える
"""

def upgrade():
    op.create_table('topic2kind',
                    sa.Column('topic_id', sa.Integer(), nullable=True),
                    sa.Column('kind_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['kind_id'], ['kind.id'], ),
                    sa.ForeignKeyConstraint(['topic_id'], ['topic.id'], ),
                    sa.PrimaryKeyConstraint()
                    )
    op.create_table('topcontent2kind',
                    sa.Column('topcontent_id', sa.Integer(), nullable=True),
                    sa.Column('kind_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['kind_id'], ['kind.id'], ),
                    sa.ForeignKeyConstraint(['topcontent_id'], ['topcontent.id'], ),
                    sa.PrimaryKeyConstraint()
                    )
    op.add_column(u'promotion', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column(u'promotion', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.drop_column(u'promotion', u'thumbnail_id')

    op.drop_constraint("fk_topcontent_bound_page_id_to_pagesets_id", "topcontent", type="foreignkey")
    op.drop_constraint("fk_topic_bound_page_id_to_pagesets_id", "topic", type="foreignkey")
    op.drop_constraint("fk_topic_event_id_to_event_id", "topic", type="foreignkey")

    op.drop_column(u'topcontent', u'kind')
    op.drop_column(u'topcontent', u'is_global')
    op.drop_column(u'topcontent', u'subkind')
    op.drop_column(u'topic', u'event_id')
    op.drop_column(u'topic', u'kind')
    op.drop_column(u'topic', u'is_global')
    op.drop_column(u'topic', u'subkind')

    op.drop_column(u'topcontent', u'bound_page_id')
    op.drop_column(u'topic', u'bound_page_id')

def downgrade():
    op.add_column(u'topic', sa.Column(u'bound_page_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topic', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topic', sa.Column(u'is_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topic', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topic', sa.Column(u'event_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'bound_page_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'is_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.create_foreign_key("fk_topcontent_bound_page_id_to_pagesets_id", 
                          "topcontent", "pagesets", ["bound_page_id"], ["id"])
    op.create_foreign_key("fk_topic_bound_page_id_to_pagesets_id", 
                          "topic", "pagesets", ["bound_page_id"], ["id"])
    op.create_foreign_key("fk_topic_event_id_to_event_id", 
                          "topic", "event", ["event_id"], ["id"])
    op.add_column(u'promotion', sa.Column(u'thumbnail_id', mysql.INTEGER(display_width=11), nullable=True))
    op.drop_column(u'promotion', 'updated_at')
    op.drop_column(u'promotion', 'created_at')
    op.drop_table('topcontent2kind')
    op.drop_table('topic2kind')

