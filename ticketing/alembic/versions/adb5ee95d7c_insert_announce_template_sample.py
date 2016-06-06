# -*- coding: utf-8 -*-

"""Insert announce template sample

Revision ID: adb5ee95d7c
Revises: 4f8e39214b0f
Create Date: 2016-06-06 16:58:04.611709

"""

# revision identifiers, used by Alembic.
revision = 'adb5ee95d7c'
down_revision = '4f8e39214b0f'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql.expression import text
from sqlalchemy.sql import functions as sqlf

Identifier = sa.BigInteger


def upgrade():
    op.execute(u"INSERT INTO AnnouncementTemplate (`id`, `organization_id`, `name`, `description`, `subject`, `message`, `sort`) VALUES (1, 15, 'pre', '発売開始前日の17:00', '[楽天チケット] まもなく発売開始 ({{event.title}})', '@@name@@ 様\n\n楽天チケット・お気に入りメールです。\n\n@@keyword@@をお気に入り登録された方に関連情報をお送りしています。\n\n{{event.title}}\n\n{{sales_segment.name}}\n発売開始日時 {{sales_segment.start_at}}\n\n詳細はこちら\n@@url@@\n\n-- \n楽天チケット\n\n', 1), (2, 15, 'end', '発売終了の3日前17:00', '[楽天チケット] まもなく販売終了 ({{event.title}})', '@@name@@ 様\n\n楽天チケット・お気に入りメールです。\n\n@@keyword@@をお気に入り登録された方に関連情報をお送りしています。\n\n{{event.title}}\n\n{{sales_segment.name}}\n発売開始日時 {{sales_segment.start_at}}\n\n詳細はこちら\n@@url@@\n\n-- \n楽天チケット\n\n', 3), (3, 15, 'just', '発売開始の3時間後', '[楽天チケット] 発売開始しました ({{event.title}})', '@@name@@ 様\n\n楽天チケット・お気に入りメールです。\n\n@@keyword@@をお気に入り登録された方に関連情報をお送りしています。\n\n{{event.title}}\n\n{{sales_segment.name}}\n発売開始日時 {{sales_segment.start_at}}\n\n詳細はこちら\n@@url@@\n\n-- \n楽天チケット\n\n', 2)")

def downgrade():
    op.execute(u"DELETE FROM AnnouncementTemplate WHERE ID IN (1,2,3)")
