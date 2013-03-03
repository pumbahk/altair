"""drop needless topic, topicontent, promotion

Revision ID: 3624a7d0cf21
Revises: 141a155153a3
Create Date: 2013-02-05 11:05:22.379924

"""

# revision identifiers, used by Alembic.
revision = '3624a7d0cf21'
down_revision = '3624a7d0cf20'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.drop_constraint("fk_topcontent_bound_page_id_to_pagesets_id", "topcontent", type="foreignkey")
    op.drop_constraint("fk_topic_bound_page_id_to_pagesets_id", "topic", type="foreignkey")
    op.drop_constraint("fk_topic_event_id_to_event_id", "topic", type="foreignkey")
    op.drop_constraint("promotion2kind_ibfk_1", "promotion2kind", type="foreignkey")
    op.drop_constraint("promotion2kind_ibfk_2", "promotion2kind", type="foreignkey")
    op.drop_table(u'kind')
    op.drop_table(u'promotion2kind')
    op.drop_column(u'promotion', u'publish_close_on')
    op.drop_column(u'promotion', u'thumbnail_id')
    op.drop_column(u'promotion', u'display_order')
    op.drop_column(u'promotion', u'publish_open_on')
    op.drop_column(u'promotion', u'is_vetoed')
    op.drop_column(u'topcontent', u'kind')
    op.drop_column(u'topcontent', u'is_global')
    op.drop_column(u'topcontent', u'is_vetoed')
    op.drop_column(u'topcontent', u'publish_close_on')
    op.drop_column(u'topcontent', u'created_at')
    op.drop_column(u'topcontent', u'updated_at')
    op.drop_column(u'topcontent', u'bound_page_id')
    op.drop_column(u'topcontent', u'publish_open_on')
    op.drop_column(u'topcontent', u'subkind')
    op.drop_column(u'topcontent', u'display_order')
    op.drop_column(u'topic', u'kind')
    op.drop_column(u'topic', u'is_global')
    op.drop_column(u'topic', u'is_vetoed')
    op.drop_column(u'topic', u'publish_close_on')
    op.drop_column(u'topic', u'created_at')
    op.drop_column(u'topic', u'updated_at')
    op.drop_column(u'topic', u'bound_page_id')
    op.drop_column(u'topic', u'event_id')
    op.drop_column(u'topic', u'publish_open_on')
    op.drop_column(u'topic', u'subkind')
    op.drop_column(u'topic', u'display_order')
    op.drop_column(u'widget_promotion', u'kind_id')
    op.drop_column(u'widget_topic', u'kind')
    op.drop_column(u'widget_topic', u'display_event')
    op.drop_column(u'widget_topic', u'topic_type')
    op.drop_column(u'widget_topic', u'display_page')
    op.drop_column(u'widget_topic', u'display_global')
    op.drop_column(u'widget_topic', u'subkind')

def downgrade():
    op.add_column(u'widget_topic', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'widget_topic', sa.Column(u'display_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'widget_topic', sa.Column(u'display_page', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'widget_topic', sa.Column(u'topic_type', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'widget_topic', sa.Column(u'display_event', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'widget_topic', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'widget_promotion', sa.Column(u'kind_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topic', sa.Column(u'display_order', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topic', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topic', sa.Column(u'publish_open_on', sa.DATETIME(), nullable=True))
    op.add_column(u'topic', sa.Column(u'event_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topic', sa.Column(u'bound_page_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topic', sa.Column(u'updated_at', sa.DATETIME(), nullable=True))
    op.add_column(u'topic', sa.Column(u'created_at', sa.DATETIME(), nullable=True))
    op.add_column(u'topic', sa.Column(u'publish_close_on', sa.DATETIME(), nullable=True))
    op.add_column(u'topic', sa.Column(u'is_vetoed', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topic', sa.Column(u'is_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topic', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'display_order', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'subkind', mysql.VARCHAR(length=255), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'publish_open_on', sa.DATETIME(), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'bound_page_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'updated_at', sa.DATETIME(), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'created_at', sa.DATETIME(), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'publish_close_on', sa.DATETIME(), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'is_vetoed', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'is_global', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'topcontent', sa.Column(u'kind', mysql.VARCHAR(length=255), nullable=True))
    op.create_foreign_key("fk_topcontent_bound_page_id_to_pagesets_id", 
                          "topcontent", "pagesets", ["bound_page_id"], ["id"])
    op.create_foreign_key("fk_topic_bound_page_id_to_pagesets_id", 
                          "topic", "pagesets", ["bound_page_id"], ["id"])
    op.create_foreign_key("fk_topic_event_id_to_event_id", 
                          "topic", "event", ["event_id"], ["id"])
    op.add_column(u'promotion', sa.Column(u'is_vetoed', mysql.TINYINT(display_width=1), nullable=True))
    op.add_column(u'promotion', sa.Column(u'publish_open_on', sa.DATETIME(), nullable=True))
    op.add_column(u'promotion', sa.Column(u'display_order', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'promotion', sa.Column(u'thumbnail_id', mysql.INTEGER(display_width=11), nullable=True))
    op.add_column(u'promotion', sa.Column(u'publish_close_on', sa.DATETIME(), nullable=True))
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
