# -*- coding:utf-8 -*-
"""add cascading option

Revision ID: 10682b0e9b28
Revises: 34639b5a1e44
Create Date: 2013-08-06 15:31:42.845782

"""

# revision identifiers, used by Alembic.
revision = '10682b0e9b28'
down_revision = '34639b5a1e44'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.exc import InternalError

import contextlib

@contextlib.contextmanager
def drop_or_skip_fk():
    try:
        yield
    except InternalError as e:
        if not "(errno: 152)" in str(e):
            raise
        
def upgrade():
    op.drop_constraint("widget_ticket_list_target_performance_id_performance_id_fk", "widget_ticketlist", type="foreignkey")
    op.create_foreign_key("widget_ticket_list_target_performance_id_performance_id_fk", "widget_ticketlist", "performance", ["target_performance_id"], ["id"], ondelete="SET NULL")
    op.drop_constraint("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", type="foreignkey")
    op.create_foreign_key("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", "sale", ["target_salessegment_id"], ["id"], ondelete="SET NULL")

    with drop_or_skip_fk():
        op.drop_constraint("widget_calendar_salessegment_id_salessegment_group_id_fk", "widget_calendar", type="foreignkey")
    op.execute("update widget_calendar wc left outer join salessegment_group as sg on wc.salessegment_id = sg.id set wc.salessegment_id = NULL where sg.id is NULL and wc.salessegment_id is not NULL;")
    op.create_foreign_key("widget_calendar_salessegment_id_salessegment_group_id_fk", "widget_calendar", "salessegment_group", ["salessegment_id"], ["id"], ondelete="SET NULL")

    with drop_or_skip_fk():
        op.drop_constraint("widget_summary_bound_event_id_event_id_fk", "widget_summary", type="foreignkey")
    op.create_foreign_key("widget_summary_bound_event_id_event_id_fk", "widget_summary", "event", ["bound_event_id"], ["id"], ondelete="SET NULL")
    
    op.drop_constraint("fk_widget_movie_asset_id_to_asset_id", "widget_movie", type="foreignkey")
    op.create_foreign_key("fk_widget_movie_asset_id_to_asset_id", "widget_movie", "asset", ["asset_id"], ["id"], ondelete="SET NULL")

    op.drop_constraint("fk_widget_image_asset_id_to_asset_id", "widget_image", type="foreignkey")
    op.create_foreign_key("fk_widget_image_asset_id_to_asset_id", "widget_image", "asset", ["asset_id"], ["id"], ondelete="SET NULL")

    op.drop_constraint("fk_widget_flash_asset_id_to_asset_id", "widget_flash", type="foreignkey")
    op.create_foreign_key("fk_widget_flash_asset_id_to_asset_id", "widget_flash", "asset", ["asset_id"], ["id"], ondelete="SET NULL")

    op.drop_constraint("widget_promotion_ibfk_3", "widget_promotion", type="foreignkey")
    op.create_foreign_key("widget_promotion_ibfk_3", "widget_promotion", "topiccoretag", ["system_tag_id"], ["id"], ondelete="SET NULL")

    with drop_or_skip_fk():
        op.drop_constraint("widget_promotion_ibfk_4", "widget_promotion", type="foreignkey")
    op.create_foreign_key("widget_promotion_ibfk_4", "widget_promotion", "topiccoretag", ["tag_id"], ["id"]) #page tagは消そうとした時エラーになってほしい

    with drop_or_skip_fk():
        op.drop_constraint("widget_topic_ibfk_2", "widget_topic", type="foreignkey")
    op.execute("delete from widget_topic where id in (select wid from (select wt.id as wid from widget_topic wt left outer join topiccoretag tag on wt.tag_id = tag.id where tag.id is NULL and wt.tag_id is not NULL) as w);")
    op.create_foreign_key("widget_topic_ibfk_2", "widget_topic", "topiccoretag", ["tag_id"], ["id"]) #tagは消そうとした時エラーになってほしい

    with drop_or_skip_fk():
        op.drop_constraint("widget_topcontent_ibfk_2", "widget_topcontent", type="foreignkey")
    op.execute("delete from widget_topcontent where id in (select wid from (select wt.id as wid from widget_topcontent wt left outer join topiccoretag tag on wt.tag_id = tag.id where tag.id is NULL and wt.tag_id is not NULL) as w);")
    op.create_foreign_key("widget_topcontent_ibfk_2", "widget_topcontent", "topiccoretag", ["tag_id"], ["id"]) #tagは消そうとした時エラーになってほしい

    

def downgrade():
    op.drop_constraint("widget_ticket_list_target_performance_id_performance_id_fk", "widget_ticketlist", type="foreignkey")
    op.create_foreign_key("widget_ticket_list_target_performance_id_performance_id_fk", "widget_ticketlist", "performance", ["target_performance_id"], ["id"])
    op.drop_constraint("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", type="foreignkey")
    op.create_foreign_key("widget_ticket_list_target_sale_id_sale_id_fk", "widget_ticketlist", "sale", ["target_salessegment_id"], ["id"])

    op.drop_constraint("widget_calendar_salessegment_id_salessegment_group_id_fk", "widget_calendar", type="foreignkey")
    op.create_foreign_key("widget_calendar_salessegment_id_salessegment_group_id_fk", "widget_calendar", "salessegment_group", ["salessegment_id"], ["id"])

    op.drop_constraint("widget_summary_bound_event_id_event_id_fk", "widget_summary", type="foreignkey")
    op.create_foreign_key("widget_summary_bound_event_id_event_id_fk", "widget_summary", "event", ["bound_event_id"], ["id"])

    op.drop_constraint("fk_widget_movie_asset_id_to_asset_id", "widget_movie", type="foreignkey")
    op.create_foreign_key("fk_widget_movie_asset_id_to_asset_id", "widget_movie", "asset", ["asset_id"], ["id"])

    op.drop_constraint("fk_widget_image_asset_id_to_asset_id", "widget_image", type="foreignkey")
    op.create_foreign_key("fk_widget_image_asset_id_to_asset_id", "widget_image", "asset", ["asset_id"], ["id"])

    op.drop_constraint("fk_widget_flash_asset_id_to_asset_id", "widget_flash", type="foreignkey")
    op.create_foreign_key("fk_widget_flash_asset_id_to_asset_id", "widget_flash", "asset", ["asset_id"], ["id"])

    op.drop_constraint("widget_promotion_ibfk_3", "widget_promotion", type="foreignkey")
    op.create_foreign_key("widget_promotion_ibfk_3", "widget_promotion", "topiccoretag", ["system_tag_id"], ["id"])

    op.drop_constraint("widget_promotion_ibfk_4", "widget_promotion", type="foreignkey")
    op.create_foreign_key("widget_promotion_ibfk_4", "widget_promotion", "topiccoretag", ["tag_id"], ["id"])

    op.drop_constraint("widget_topic_ibfk_2", "widget_topic", type="foreignkey")
    op.create_foreign_key("widget_topic_ibfk_2", "widget_topic", "topiccoretag", ["tag_id"], ["id"])

    op.drop_constraint("widget_topcontent_ibfk_2", "widget_topcontent", type="foreignkey")
    op.create_foreign_key("widget_topcontent_ibfk_2", "widget_topcontent", "topiccoretag", ["tag_id"], ["id"])

    
