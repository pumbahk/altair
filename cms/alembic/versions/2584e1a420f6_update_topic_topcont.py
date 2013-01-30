# -*- coding:utf-8 -*-
"""update topic topcontent

Revision ID: 2584e1a420f6
Revises: 5a8a6eccba80
Create Date: 2013-01-29 18:53:53.819831

"""

# revision identifiers, used by Alembic.
revision = '2584e1a420f6'
down_revision = '5a8a6eccba80'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_constraint("fk_topcontent_bound_page_id_to_pagesets_id", "topcontent", type="foreignkey")
    op.drop_constraint("fk_topic_bound_page_id_to_pagesets_id", "topic", type="foreignkey")
    op.drop_constraint("fk_topic_event_id_to_event_id", "topic", type="foreignkey")

    ## relation無いかもしれない
    op.drop_constraint("promotion2kind_ibfk_1", "promotion2kind", type="foreignkey")
    op.drop_constraint("promotion2kind_ibfk_2", "promotion2kind", type="foreignkey")

    op.create_table('promotiontag',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topcontenttag',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topictag',
                    sa.Column('organization_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topictag2topic',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['topic.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['topictag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('promotiontag2promotion',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['promotion.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['promotiontag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topcontenttag2topcontent',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['topcontent.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['topcontenttag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )

    op.drop_table(u'kind')
    op.drop_table(u'promotion2kind')
    op.add_column(u'promotion', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column(u'promotion', sa.Column('updated_at', sa.DateTime(), nullable=True))
    op.drop_column(u'promotion', u'thumbnail_id')
    op.drop_column(u'topcontent', u'kind')
    op.drop_column(u'topcontent', u'is_global')
    op.drop_column(u'topcontent', u'subkind')
    op.drop_column(u'topcontent', u'bound_page_id')
    op.drop_column(u'topic', u'event_id')
    op.drop_column(u'topic', u'kind')
    op.drop_column(u'topic', u'is_global')
    op.drop_column(u'topic', u'subkind')
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
    op.create_table(u'kind',
                    sa.Column(u'organization_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
                    sa.Column(u'id', mysql.INTEGER(display_width=11), nullable=False),
                    sa.Column(u'name', mysql.VARCHAR(length=255), nullable=True),
                    sa.PrimaryKeyConstraint(u'id')
                    )
    op.create_table(u'promotion2kind',
                    sa.Column(u'promotion_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
                    sa.Column(u'kind_id', mysql.INTEGER(display_width=11), autoincrement=False, nullable=True),
                    sa.ForeignKeyConstraint(['kind_id'], [u'kind.id'], name=u'promotion2kind_ibfk_1'),
                    sa.ForeignKeyConstraint(['promotion_id'], [u'promotion.id'], name=u'promotion2kind_ibfk_2'),
                    sa.PrimaryKeyConstraint()
                    )

    op.drop_table('topcontenttag2topcontent')
    op.drop_table('promotiontag2promotion')
    op.drop_table('topictag2topic')
    op.drop_table('topictag')
    op.drop_table('topcontenttag')
    op.drop_table('promotiontag')
