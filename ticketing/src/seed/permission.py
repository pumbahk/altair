# -*- coding: utf-8 -*-

from seed import DataSet

class PermissionData(DataSet):
    class everyone:
        category_name =  'everyone'
        permit = 1
    class administrator:
        ''' 管理者　administrator '''
        category_name =  'administrator'
        permit = 1
    class event_viewer:
        ''' イベント閲覧者　event_viewer '''
        category_name =  'event_viewer'
        permit = 1
    class event_editor:
        ''' イベント編集者　event_editor '''
        category_name =  'event_editor'
        permit = 1
    class topic_viewer:
        ''' トピック閲覧者　topic_viewer '''
        category_name =  'topic_viewer'
        permit = 1
    class ticket_editor:
        ''' チケット編集者　ticket_editor '''
        category_name =  'ticket_editor'
        permit = 1
    class magazine_viewer:
        ''' メルマガ閲覧者　magazine_viewer '''
        category_name =  'magazine_viewer'
        permit = 1
    class magazine_editor:
        ''' メルマガ編集者　magazine_editor '''
        category_name =  'magazine_editor'
        permit = 1
    class asset_viewer:
        ''' アセット閲覧者　asset_viewer '''
        category_name =  'asset_viewer'
        permit = 1
    class asset_editor:
        ''' アセット編集者　asset_editor '''
        category_name =  'asset_editor'
        permit = 1
    class page_viewer:
        ''' ページ閲覧者　page_viewer '''
        category_name =  'page_viewer'
        permit = 1
    class page_editor:
        ''' ページ編集者　page_editor '''
        category_name =  'page_editor'
        permit = 1
    class tag_viewer:
        ''' タグ閲覧者　tag_viewer '''
        category_name =  'page_editor'
        permit = 1
    class tag_editor:
        ''' タグ編集者　tag_editor '''
        category_name =  'tag_editor'
        permit = 1
    class layout_viewer:
        ''' レイアウト閲覧者　layout_viewer '''
        category_name =  'layout_viewer'
        permit = 1

    class layout_editor:
        ''' レイアウト編集者　layout_editor '''
        category_name =  'layout_editor'
        permit = 1
