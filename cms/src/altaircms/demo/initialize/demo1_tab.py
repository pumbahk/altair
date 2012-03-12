# -*- coding:utf-8 -*-

import datetime
import os

from pyramid.testing import DummyRequest
import transaction

from altaircms.models import DBSession
from . import append_to_json_structure
from . import block

"""
tab check,  image gallery
"""

here = os.path.abspath(os.path.dirname(__file__))
def add_widget(page):
    with block("menu"):
        from altaircms.plugins.widget.menu.views import MenuWidgetView
        from altaircms.plugins.widget.menu.models import MenuWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id)
        context = MenuWidgetResource(request)
        request.context = context
        r = MenuWidgetView(request).create()
        append_to_json_structure(page, "page_main_title", 
                                 {"name": "menu", "pk": r["pk"]})


    from altaircms.asset.models import ImageAsset
    asset = ImageAsset.query.first()
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})
    with block("image"):
        from altaircms.plugins.widget.image.views import ImageWidgetView
        from altaircms.plugins.widget.image.models import ImageWidgetResource
        request = DummyRequest()
        request.json_body = dict(page_id=page.id, data=dict(asset_id=asset.id))
        context = ImageWidgetResource(request)
        request.context = context
        r = ImageWidgetView(request).create()
        append_to_json_structure(page, "page_main_main", 
                                 {"name": "image", "pk": r["pk"]})


def init():
        ## page
        from altaircms.page.models import Page
        D = {'created_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438062),
             'description': u'松下奈緒コンサートツアー2012　for meの公演についての詳細、チケット予約',
             'event_id': 1,
             'keywords': u'チケット,演劇,クラシック,オペラ,コンサート,バレエ,ミュージカル,野球,サッカー,格闘技',
             'layout_id': 2,
             'parent_id': None,
             'site_id': None,
             'title': u'松下奈緒コンサートツアー2012　画像ギャラリー',
             'updated_at': datetime.datetime(2012, 2, 14, 15, 13, 26, 438156),
             'url': u'demo1_gallery',
             "structure": "{}", 
             'version': None}
        page = Page.from_dict(D)
        DBSession.add(page)
        add_widget(page)
        transaction.commit()

    
