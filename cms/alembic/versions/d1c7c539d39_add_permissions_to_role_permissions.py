"""add permissions to role_permissions

Revision ID: d1c7c539d39
Revises: 3c0b248aad83
Create Date: 2015-05-18 10:42:46.806399

"""

# revision identifiers, used by Alembic.
revision = 'd1c7c539d39'
down_revision = '3c0b248aad83'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

old_options = ('event_create','event_read','event_update','event_delete','topic_create','topic_read','topic_update','topic_delete',
                'topcontent_create','topcontent_read','topcontent_update','topcontent_delete','ticket_create','ticket_read','ticket_update',
                'ticket_delete','magazine_create','magazine_read','magazine_update','magazine_delete','asset_create','asset_read','asset_update',
                'asset_delete','page_create','page_read','page_update','page_delete','tag_create','tag_read','tag_update','tag_delete','category_create',
                'category_read','category_update','category_delete','promotion_create','promotion_read','promotion_update','promotion_delete',
                'promotion_unit_create','promotion_unit_read','promotion_unit_update','promotion_unit_delete','sale_create','sale_read','sale_update',
                'sale_delete','performance_create','performance_read','performance_update','performance_delete','layout_create','layout_read','layout_update',
                'layout_delete','operator_create','operator_read','operator_update','operator_delete','hotword_create','hotword_read','hotword_update','hotword_delete',
                'pagedefaultinfo_create','pagedefaultinfo_read','pagedefaultinfo_update','pagedefaultinfo_delete',  'important_page_create',  'important_page_read',)

new_options = (old_options + ('organization_create','host_create',))

old_type = sa.Enum(*old_options, name='name')
new_type = sa.Enum(*new_options, name='name')


def upgrade():
    op.alter_column('role_permissions', 'name', type_=new_type)

def downgrade():
    op.alter_column('role_permissions', 'name', type_=old_type)
