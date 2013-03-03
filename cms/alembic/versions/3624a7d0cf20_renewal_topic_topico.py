# -*- coding:utf-8 -*-
"""renewal topic,topicontent, promotion

Revision ID: 3624a7d0cf20
Revises: 141a155153a3
Create Date: 2013-02-05 11:05:22.379924

"""

# revision identifiers, used by Alembic.
revision = '3624a7d0cf20'
down_revision = '4bc26f9dc2a0'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.create_table('widget_topcontent',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('display_type', sa.Unicode(length=255), nullable=True),
                    sa.Column('display_count', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], ),
                    sa.ForeignKeyConstraint(['tag_id'], ['topiccoretag.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.add_column(u'widget_promotion', sa.Column('tag_id', sa.Integer(), nullable=True))
    op.add_column(u'widget_topic', sa.Column('display_type', sa.Unicode(length=255), nullable=True))
    op.add_column(u'widget_topic', sa.Column('tag_id', sa.Integer(), nullable=True))

    ## data migration
    op.execute(u'update widget_topic set display_type = "89ers_faq" where kind = "89ers質問";')
    op.execute(u'update widget_topic set display_type = "nh_faq" where kind = "NH質問";')
    op.execute(u'update widget_topic set display_type = "cr_faq" where kind = "CR質問";')
    op.execute(u'update widget_topic set display_type = "vissel_faq" where kind = "vissel質問";')
    op.execute(u'update widget_topic set display_type = "topic" where kind = "注目のイベント";')

    op.execute(u'update widget_topic as target join (select wt.id, tag.id as tag_id, wt.subkind, p.organization_id from widget_topic as wt join widget as w on wt.id=w.id join page as p on w.page_id=p.id join topiccoretag as tag on tag.organization_id = p.organization_id where tag.label=wt.subkind and tag.type="topic") as cand on target.id = cand.id set target.tag_id = cand.tag_id where target.subkind = cand.subkind;')
    
def downgrade():
    op.drop_column(u'widget_topic', 'tag_id')
    op.drop_column(u'widget_topic', 'display_type')
    op.drop_column(u'widget_promotion', 'tag_id')
    op.drop_table('widget_topcontent')
