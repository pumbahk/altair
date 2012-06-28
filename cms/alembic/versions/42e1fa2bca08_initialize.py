"""initialize

Revision ID: 42e1fa2bca08
Revises: None
Create Date: 2012-06-08 16:05:26.825217

"""

# revision identifiers, used by Alembic.
revision = '42e1fa2bca08'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('role',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('assettag',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('type', sa.String(length=32), nullable=False),
                    sa.CheckConstraint('TODO'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('label','type','publicp')
                    )
    op.create_table('pagetag',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('publicp', sa.Boolean(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('label','publicp')
                    )
    op.create_table('client',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('prefecture', sa.Unicode(length=255), nullable=True),
                    sa.Column('address', sa.Unicode(length=255), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('contract_status', sa.Integer(), nullable=True),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('oauth_token',
                    sa.Column('token', sa.String(length=255), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.PrimaryKeyConstraint('token')
                    )
    op.create_table('apikey',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('apikey', sa.String(length=255), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_apikey_client_id_to_client_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('operator',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('auth_source', sa.String(length=255), nullable=False),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.Column('screen_name', sa.Unicode(length=255), nullable=True),
                    sa.Column('oauth_token', sa.String(length=255), nullable=True),
                    sa.Column('oauth_token_secret', sa.String(length=255), nullable=True),
                    sa.Column('date_joined', sa.DateTime(), nullable=True),
                    sa.Column('last_login', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_operator_client_id_to_client_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('role_permissions',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Enum('event_create', 'event_read', 'event_update', 'event_delete', 'topic_create', 'topic_read', 'topic_update', 'topic_delete', 'topcontent_create', 'topcontent_read', 'topcontent_update', 'topcontent_delete', 'ticket_create', 'ticket_read', 'ticket_update', 'ticket_delete', 'magazine_create', 'magazine_read', 'magazine_update', 'magazine_delete', 'asset_create', 'asset_read', 'asset_update', 'asset_delete', 'page_create', 'page_read', 'page_update', 'page_delete', 'tag_create', 'tag_read', 'tag_update', 'tag_delete', 'category_create', 'category_read', 'category_update', 'category_delete', 'promotion_create', 'promotion_read', 'promotion_update', 'promotion_delete', 'promotion_unit_create', 'promotion_unit_read', 'promotion_unit_update', 'promotion_unit_delete', 'sale_create', 'sale_read', 'sale_update', 'sale_delete', 'performance_create', 'performance_read', 'performance_update', 'performance_delete', 'layout_create', 'layout_read', 'layout_update', 'layout_delete', 'operator_create', 'operator_read', 'operator_update', 'operator_delete', 'hotword_create', 'hotword_read', 'hotword_update', 'hotword_delete', 'pagedefaultinfo_create', 'pagedefaultinfo_read', 'pagedefaultinfo_update', 'pagedefaultinfo_delete'), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name="fk_role_permissions_role_id_to_role_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('event',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('backend_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('subtitle', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.Column('place', sa.Unicode(length=255), nullable=True),
                    sa.Column('inquiry_for', sa.Unicode(length=255), nullable=True),
                    sa.Column('event_open', sa.DateTime(), nullable=True),
                    sa.Column('event_close', sa.DateTime(), nullable=True),
                    sa.Column('deal_open', sa.DateTime(), nullable=True),
                    sa.Column('deal_close', sa.DateTime(), nullable=True),
                    sa.Column('is_searchable', sa.Boolean(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_event_client_id_to_client_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('site',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_site_client_id_to_client_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('asset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('type', sa.String(length=32), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('created_by_id', sa.Integer(), nullable=True),
                    sa.Column('updated_by_id', sa.Integer(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['created_by_id'], ['operator.id'], name="fk_asset_created_by_id_to_operator_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], ),
                    sa.ForeignKeyConstraint(['updated_by_id'], ['operator.id'], name="fk_asset_updated_by_id_to_operator_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('operator_role',
                    sa.Column('operator_id', sa.Integer(), nullable=True),
                    sa.Column('role_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['operator_id'], ['operator.id'], name="fk_operator_role_operator_id_to_operator_id"),
                    sa.ForeignKeyConstraint(['role_id'], ['role.id'], name="fk_operator_role_role_id_to_role_id"),
                    sa.PrimaryKeyConstraint()
                    )
    op.create_table('widgetdisposition',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('structure', sa.String(length=255), nullable=True),
                    sa.Column('blocks', sa.String(length=255), nullable=True),
                    sa.Column('is_public', sa.Boolean(), nullable=True),
                    sa.Column('owner_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['owner_id'], ['operator.id'], name="fk_widgetdisposition_owner_id_to_operator_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_widgetdisposition_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('pagesets',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('version_counter', sa.Integer(), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('parent_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name="fk_pagesets_event_id_to_event_id"),
                    sa.ForeignKeyConstraint(['parent_id'], ['pagesets.id'], name="fk_pagesets_parent_id_to_pagesets_id"),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('url')
                    )
    op.create_table('promotion',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_promotion_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('layout',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('title', sa.String(length=255), nullable=True),
                    sa.Column('template_filename', sa.String(length=255), nullable=True),
                    sa.Column('blocks', sa.Text(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_layout_client_id_to_client_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_layout_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('hotword',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('enablep', sa.Boolean(), nullable=True),
                    sa.Column('term_begin', sa.DateTime(), nullable=True),
                    sa.Column('term_end', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_hotword_site_id_to_site_id"),
                    sa.ForeignKeyConstraint(['tag_id'], ['pagetag.id'], name="fk_hotword_tag_id_to_pagetag_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('performance',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('backend_id', sa.Integer(), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('venue', sa.Unicode(length=255), nullable=True),
                    sa.Column('prefecture', sa.Enum('hokkaido', 'aomori', 'iwate', 'miyagi', 'akita', 'yamagata', 'fukushima', 'ibaraki', 'tochigi', 'gunma', 'saitama', 'chiba', 'tokyo', 'kanagawa', 'niigata', 'toyama', 'ishikawa', 'fukui', 'yamanashi', 'nagano', 'gifu', 'shizuoka', 'aichi', 'mie', 'shiga', 'kyoto', 'osaka', 'hyogo', 'nara', 'wakayama', 'tottori ', 'shimane', 'okayama', 'hiroshima', 'yamaguchi', 'tokushima', 'kagawa', 'ehime', 'kouchi', 'fukuoka', 'saga', 'nagasaki', 'kumamoto', 'oita', 'miyazaki', 'kagoshima', 'okinawa'), nullable=True),
                    sa.Column('open_on', sa.DateTime(), nullable=True),
                    sa.Column('start_on', sa.DateTime(), nullable=True),
                    sa.Column('end_on', sa.DateTime(), nullable=True),
                    sa.Column('purchase_link', sa.UnicodeText(), nullable=True),
                    sa.Column('canceld', sa.Boolean(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_performance_client_id_to_client_id"),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name="fk_performance_event_id_to_event_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('user',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('email', sa.String(length=255), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('is_active', sa.Integer(), nullable=True),
                    sa.Column('is_administrator', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_user_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('flash_asset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('alt', sa.Integer(), nullable=True),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('filepath', sa.String(length=255), nullable=True),
                    sa.Column('mimetype', sa.String(length=255), nullable=True),
                    sa.Column('imagepath', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['asset.id'], name="fk_flash_asset_id_to_asset_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('sale',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('performance_id', sa.Integer(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('start_on', sa.DateTime(), nullable=True),
                    sa.Column('end_on', sa.DateTime(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name="fk_sale_event_id_to_event_id"),
                    sa.ForeignKeyConstraint(['performance_id'], ['performance.id'], name="fk_sale_performance_id_to_performance_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('assettag2asset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['asset.id'], name="fk_assettag2asset_object_id_to_asset_id"),
                    sa.ForeignKeyConstraint(['tag_id'], ['assettag.id'], name="fk_assettag2asset_tag_id_to_asset_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('movie_asset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('alt', sa.Integer(), nullable=True),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('filepath', sa.String(length=255), nullable=True),
                    sa.Column('mimetype', sa.String(length=255), nullable=True),
                    sa.Column('imagepath', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['asset.id'], name="fk_movie_asset_id_to_asset_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('category',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('parent_id', sa.Integer(), nullable=True),
                    sa.Column('label', sa.Unicode(length=255), nullable=True),
                    sa.Column('name', sa.String(length=255), nullable=True),
                    sa.Column('imgsrc', sa.String(length=255), nullable=True),
                    sa.Column('hierarchy', sa.Unicode(length=255), nullable=False),
                    sa.Column('url', sa.Unicode(length=255), nullable=True),
                    sa.Column('pageset_id', sa.Integer(), nullable=True),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('origin', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['pageset_id'], ['pagesets.id'], name="fk_category_pageset_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['parent_id'], ['category.id'], name="fk_category_parent_id_to_category_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_category_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('image_asset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('alt', sa.Integer(), nullable=True),
                    sa.Column('size', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('filepath', sa.String(length=255), nullable=True),
                    sa.Column('mimetype', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['asset.id'], name="fk_image_asset_id_to_asset_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topic',
                    sa.Column('publish_open_on', sa.DateTime(), nullable=True),
                    sa.Column('publish_close_on', sa.DateTime(), nullable=True),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('is_vetoed', sa.Boolean(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('subkind', sa.Unicode(length=255), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('text', sa.UnicodeText(), nullable=True),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('linked_page_id', sa.Integer(), nullable=True),
                    sa.Column('bound_page_id', sa.Integer(), nullable=True),
                    sa.Column('is_global', sa.Boolean(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['bound_page_id'], ['pagesets.id'], name="fk_topic_bound_page_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_topic_client_id_to_client_id"),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name="fk_topic_event_id_to_event_id"),
                    sa.ForeignKeyConstraint(['linked_page_id'], ['pagesets.id'], name="fk_topic_linked_page_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_topic_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('page',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('name', sa.Unicode(length=255), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('keywords', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.Column('url', sa.String(length=255), nullable=True),
                    sa.Column('version', sa.Integer(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('layout_id', sa.Integer(), nullable=True),
                    sa.Column('structure', sa.Text(), nullable=True),
                    sa.Column('published', sa.Boolean(), nullable=True), 
                    sa.Column('hash_url', sa.String(length=32), nullable=True),
                    sa.Column('event_id', sa.Integer(), nullable=True),
                    sa.Column('pageset_id', sa.Integer(), nullable=True),
                    sa.Column('publish_begin', sa.DateTime(), nullable=True),
                    sa.Column('publish_end', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['event_id'], ['event.id'], name="fk_page_id_to_event_id"),
                    sa.ForeignKeyConstraint(['layout_id'], ['layout.id'], name="fk_page_layout_id_to_layout_id"),
                    sa.ForeignKeyConstraint(['pageset_id'], ['pagesets.id'], name="fk_page_pageset_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_page_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    # op.create_table('mailmagazine_user',
    #                 sa.Column('id', sa.Integer(), nullable=False),
    #                 sa.Column('mailmagazine_id', sa.Integer(), nullable=True),
    #                 sa.Column('user_id', sa.Integer(), nullable=True),
    #                 sa.Column('joined_at', sa.DateTime(), nullable=True),
    #                 sa.Column('can_distribute', sa.Integer(), nullable=True),
    #                 sa.ForeignKeyConstraint(['mailmagazine_id'], ['mailmagazine.id'], name="fk_mailmagazine_user_mailmagazine_id_to_mailmagazine_id"),
    #                 sa.ForeignKeyConstraint(['user_id'], ['user.id'], name="fk_mailmagazine_user_user_id_to_user_id"),
    #                 sa.PrimaryKeyConstraint('id')
    #                 )
    # op.create_table('mailmagazine_distribute',
    #                 sa.Column('id', sa.Integer(), nullable=False),
    #                 sa.Column('mailmagazine_id', sa.Integer(), nullable=True),
    #                 sa.Column('username', sa.Unicode(length=255), nullable=True),
    #                 sa.Column('email', sa.String(length=255), nullable=True),
    #                 sa.Column('status', sa.String(length=255), nullable=True),
    #                 sa.Column('send_at', sa.DateTime(), nullable=True),
    #                 sa.ForeignKeyConstraint(['mailmagazine_id'], ['mailmagazine.id'], name="fk_mailmagazine_distribute_mailmagazine_id_to_mailmagazine_id"),
    #                 sa.PrimaryKeyConstraint('id')
    #                 )
    # op.create_table('mailmagazine',
    #                 sa.Column('id', sa.Integer(), nullable=False),
    #                 sa.Column('title', sa.Unicode(length=255), nullable=True),
    #                 sa.Column('description', sa.Unicode(length=255), nullable=True),
    #                 sa.Column('site_id', sa.Integer(), nullable=True),
    #                 sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_mailmag"),
    #                 sa.PrimaryKeyConstraint('id')
    #                 )
    op.create_table('page_default_info',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('title_fmt', sa.Unicode(length=255), nullable=True),
                    sa.Column('url_fmt', sa.Unicode(length=255), nullable=True),
                    sa.Column('pageset_id', sa.Integer(), nullable=True),
                    sa.Column('keywords', sa.Unicode(length=255), nullable=True),
                    sa.Column('description', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['pageset_id'], ['pagesets.id'], name="fk_page_default_info_pageset_id_to_pagesets_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('ticket',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('sale_id', sa.Integer(), nullable=True),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('price', sa.Integer(), nullable=True),
                    sa.Column('seattype', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['sale_id'], ['sale.id'], name="fk_ticket_sale_id_to_sale_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('pagetag2page',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('object_id', sa.Integer(), nullable=True),
                    sa.Column('tag_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['object_id'], ['page.id'], name="fk_pagetag2page_object_id_to_page_id"),
                    sa.ForeignKeyConstraint(['tag_id'], ['pagetag.id'], name="fk_pagetag2page_tag_id_to_pagetag_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('topcontent',
                    sa.Column('publish_open_on', sa.DateTime(), nullable=True),
                    sa.Column('publish_close_on', sa.DateTime(), nullable=True),
                    sa.Column('orderno', sa.Integer(), nullable=True),
                    sa.Column('is_vetoed', sa.Boolean(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('client_id', sa.Integer(), nullable=True),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('subkind', sa.Unicode(length=255), nullable=True),
                    sa.Column('title', sa.Unicode(length=255), nullable=True),
                    sa.Column('text', sa.Unicode(length=255), nullable=True),
                    sa.Column('linked_page_id', sa.Integer(), nullable=True),
                    sa.Column('bound_page_id', sa.Integer(), nullable=True),
                    sa.Column('image_asset_id', sa.Integer(), nullable=True),
                    sa.Column('countdown_type', sa.String(length=255), nullable=True),
                    sa.Column('is_global', sa.Boolean(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['bound_page_id'], ['pagesets.id'], name="fk_topcontent_bound_page_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['client_id'], ['client.id'], name="fk_topcontent_client_id_to_client_id"),
                    sa.ForeignKeyConstraint(['image_asset_id'], ['image_asset.id'], name="fk_topcontent_image_asset_id_to_image_asset_id"),
                    sa.ForeignKeyConstraint(['linked_page_id'], ['pagesets.id'], name="fk_topcontent_linked_page_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_topcontent_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('promotion_unit',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('promotion_id', sa.Integer(), nullable=True),
                    sa.Column('main_image_id', sa.Integer(), nullable=True),
                    sa.Column('thumbnail_id', sa.Integer(), nullable=True),
                    sa.Column('text', sa.UnicodeText(), nullable=True),
                    sa.Column('link', sa.Unicode(length=255), nullable=True),
                    sa.Column('pageset_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['main_image_id'], ['image_asset.id'], name="fk_promotion_unit_main_image_id_to_image_asset_id"),
                    sa.ForeignKeyConstraint(['pageset_id'], ['pagesets.id'], name="fk_promotion_unit_pageset_id_to_pagesets_id"),
                    sa.ForeignKeyConstraint(['promotion_id'], ['promotion.id'], name="fk_promotion_unit_promotion_id_promotion_id"),
                    sa.ForeignKeyConstraint(['thumbnail_id'], ['image_asset.id'], name="fk_promotion_unit_thumbnail_id_to_image_asset_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget',
                    sa.Column('page_id', sa.Integer(), nullable=True),
                    sa.Column('disposition_id', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('site_id', sa.Integer(), nullable=True),
                    sa.Column('type', sa.String(length=32), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.ForeignKeyConstraint(['disposition_id'], ['widgetdisposition.id'], name="fk_widget_disposition_id_to_widgetdisposition_id"),
                    sa.ForeignKeyConstraint(['page_id'], ['page.id'], name="fk_widget_page_id_to_page_id"),
                    sa.ForeignKeyConstraint(['site_id'], ['site.id'], name="fk_widget_site_id_to_site_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_countdown',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('kind', sa.String(length=25), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_countdown_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_promotion',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('promotion_id', sa.Integer(), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_promotion_id_to_widget_id"),
                    sa.ForeignKeyConstraint(['promotion_id'], ['promotion.id'], name="fk_widget_promotion_promotion_id_to_promotion_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_performancelist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_performancelist_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_summary',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.UnicodeText(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'],name="fk_widget_summary_id_to_widget_id" ),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_detail',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('kind', sa.String(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_detail_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_topic',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('topic_type', sa.String(length=255), nullable=True),
                    sa.Column('display_count', sa.Integer(), nullable=True),
                    sa.Column('display_global', sa.Boolean(), nullable=True),
                    sa.Column('display_event', sa.Boolean(), nullable=True),
                    sa.Column('display_page', sa.Boolean(), nullable=True),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('subkind', sa.Unicode(length=255), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.CheckConstraint('TODO'),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_topic_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_reuse',
                    sa.Column('attrs', sa.String(length=255), nullable=True),
                    sa.Column('source_page_id', sa.Integer(), nullable=True),
                    sa.Column('width', sa.Integer(), nullable=True),
                    sa.Column('height', sa.Integer(), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_reuse_id_to_widget_id"),
                    sa.ForeignKeyConstraint(['source_page_id'], ['page.id'], name="fk_widget_reuse_source_page_id_to_page_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_calendar',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('calendar_type', sa.String(length=255), nullable=True),
                    sa.Column('from_date', sa.Date(), nullable=True),
                    sa.Column('to_date', sa.Date(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_calendar_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_flash',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('asset_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['asset_id'], ['asset.id'], name="fk_widget_flash_asset_id_to_asset_id"),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_flash_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('order_history',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('created_at', sa.DateTime(), nullable=True),
                    sa.Column('updated_at', sa.DateTime(), nullable=True),
                    sa.Column('ticket_id', sa.Integer(), nullable=True),
                    sa.Column('user_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['ticket_id'], ['ticket.id'], name="order_history_ticket_id_to_ticket_id"),
                    sa.ForeignKeyConstraint(['user_id'], ['user.id'], name="order_history_user_id_to_user_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_linklist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('delimiter', sa.Unicode(length=255), nullable=True),
                    sa.Column('finder_kind', sa.Unicode(length=32), nullable=True),
                    sa.Column('max_items', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_linklist_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_menu',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('items', sa.UnicodeText(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_menu_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_breadcrumbs',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_breadcrumbs_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_iconset',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('kind', sa.String(length=32), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_iconset_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_movie',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('asset_id', sa.Integer(), nullable=True),
                    sa.ForeignKeyConstraint(['asset_id'], ['asset.id'], name="fk_widget_movie_asset_id_to_asset_id"),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_movie_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_heading',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('text', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_heading_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_anchorlist',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_anchorlist_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_purchase',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('kind', sa.Unicode(length=32), nullable=True),
                    sa.Column('external_link', sa.Unicode(length=255), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_purchase_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_image',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('href', sa.String(length=255), nullable=True),
                    sa.Column('alt', sa.Unicode(length=255), nullable=True),
                    sa.Column('asset_id', sa.Integer(), nullable=True),
                    sa.Column('nowrap', sa.Boolean(), nullable=True),
                    sa.CheckConstraint('TODO'),
                    sa.ForeignKeyConstraint(['asset_id'], ['asset.id'], name="fk_widget_image_asset_id_to_asset_id"),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_image_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_text',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('text', sa.UnicodeText(), nullable=True),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_text_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )
    op.create_table('widget_ticketlist',
                    sa.Column('kind', sa.Unicode(length=255), nullable=True),
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.ForeignKeyConstraint(['id'], ['widget.id'], name="fk_widget_ticketlist_id_to_widget_id"),
                    sa.PrimaryKeyConstraint('id')
                    )

def downgrade():
    op.drop_table('widget_ticketlist')
    op.drop_table('widget_text')
    op.drop_table('widget_image')
    op.drop_table('widget_purchase')
    op.drop_table('widget_anchorlist')
    op.drop_table('widget_heading')
    op.drop_table('widget_movie')
    op.drop_table('widget_iconset')
    op.drop_table('widget_breadcrumbs')
    op.drop_table('widget_menu')
    op.drop_table('widget_linklist')
    op.drop_table('order_history')
    op.drop_table('widget_flash')
    op.drop_table('widget_calendar')
    op.drop_table('widget_reuse')
    op.drop_table('widget_topic')
    op.drop_table('widget_detail')
    op.drop_table('widget_summary')
    op.drop_table('widget_performancelist')
    op.drop_table('widget_promotion')
    op.drop_table('widget_countdown')
    op.drop_table('widget')
    op.drop_table('promotion_unit')
    op.drop_table('topcontent')
    op.drop_table('pagetag2page')
    op.drop_table('ticket')
    op.drop_table('page_default_info')
    # op.drop_table('mailmagazine_distribute')
    # op.drop_table('mailmagazine_user')
    op.drop_table('page')
    op.drop_table('topic')
    op.drop_table('image_asset')
    op.drop_table('category')
    op.drop_table('movie_asset')
    op.drop_table('assettag2asset')
    op.drop_table('sale')
    op.drop_table('flash_asset')
    op.drop_table('user')
    op.drop_table('performance')
    op.drop_table('hotword')
    op.drop_table('layout')
    op.drop_table('promotion')
    op.drop_table('pagesets')
    op.drop_table('widgetdisposition')
    # op.drop_table('mailmagazine')
    op.drop_table('operator_role')
    op.drop_table('asset')
    op.drop_table('site')
    op.drop_table('event')
    op.drop_table('role_permissions')
    op.drop_table('operator')
    op.drop_table('apikey')
    op.drop_table('oauth_token')
    op.drop_table('client')
    op.drop_table('pagetag')
    op.drop_table('assettag')
    op.drop_table('role')
