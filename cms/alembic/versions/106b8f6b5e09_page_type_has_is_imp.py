"""page type has is_important flag

Revision ID: 106b8f6b5e09
Revises: 3ecb4baa7463
Create Date: 2013-06-03 14:30:42.605484

"""

# revision identifiers, used by Alembic.
revision = '106b8f6b5e09'
down_revision = '3ecb4baa7463'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    op.add_column('pagetype', sa.Column('is_important', sa.Boolean(), nullable=False))
    op.execute("update pagetype set is_important = 0;")
    op.execute("alter table role_permissions modify column name enum('event_create','event_read','event_update','event_delete','topic_create','topic_read','topic_update','topic_delete','topcontent_create','topcontent_read','topcontent_update','topcontent_delete','ticket_create','ticket_read','ticket_update','ticket_delete','magazine_create','magazine_read','magazine_update','magazine_delete','asset_create','asset_read','asset_update','asset_delete','page_create','page_read','page_update','page_delete','tag_create','tag_read','tag_update','tag_delete','category_create','category_read','category_update','category_delete','promotion_create','promotion_read','promotion_update','promotion_delete','promotion_unit_create','promotion_unit_read','promotion_unit_update','promotion_unit_delete','sale_create','sale_read','sale_update','sale_delete','performance_create','performance_read','performance_update','performance_delete','layout_create','layout_read','layout_update','layout_delete','operator_create','operator_read','operator_update','operator_delete','hotword_create','hotword_read','hotword_update','hotword_delete','pagedefaultinfo_create','pagedefaultinfo_read','pagedefaultinfo_update','pagedefaultinfo_delete',  'important_page_create',  'important_page_read', 'administrator');")

def downgrade():
    op.drop_column('pagetype', 'is_important')
    op.execute("alter table role_permissions modify column name enum('event_create','event_read','event_update','event_delete','topic_create','topic_read','topic_update','topic_delete','topcontent_create','topcontent_read','topcontent_update','topcontent_delete','ticket_create','ticket_read','ticket_update','ticket_delete','magazine_create','magazine_read','magazine_update','magazine_delete','asset_create','asset_read','asset_update','asset_delete','page_create','page_read','page_update','page_delete','tag_create','tag_read','tag_update','tag_delete','category_create','category_read','category_update','category_delete','promotion_create','promotion_read','promotion_update','promotion_delete','promotion_unit_create','promotion_unit_read','promotion_unit_update','promotion_unit_delete','sale_create','sale_read','sale_update','sale_delete','performance_create','performance_read','performance_update','performance_delete','layout_create','layout_read','layout_update','layout_delete','operator_create','operator_read','operator_update','operator_delete','hotword_create','hotword_read','hotword_update','hotword_delete','pagedefaultinfo_create','pagedefaultinfo_read','pagedefaultinfo_update','pagedefaultinfo_delete');")
