from datetime import datetime
from ..testing import setup_db, teardown_db

def _getImageAsset():
    from altaircms.asset.models import ImageAsset
    D = {'filepath': u'/static/img/samples/Abstract_Desktop_290.jpg',
         'id': 1,
         "page_id": 2}
    return ImageAsset.from_dict(D)


def _getTextWidget():
    from altaircms.plugins.widget.freetext.models import FreetextWidget
    D = {'id': 1, 'text': u'freetext',"page_id": 2}
    return FreetextWidget.from_dict(D)

def _getImageWidget():
    from altaircms.plugins.widget.image.models import ImageWidget
    asset = _getImageAsset()
    D = {"id": 2, "asset": asset,  "asset_id": asset.id, "page_id":2}
    return ImageWidget.from_dict(D)

def _getMenuWidget():
    from altaircms.plugins.widget.menu.models import MenuWidget
    D = {"id": 3,  "page_id":2, "items":"[]"}
    return MenuWidget.from_dict(D)


def _getPage(structure):
    from altaircms.page.models import Page
    D = {'created_at': datetime(2012, 2, 14, 15, 13, 26, 438062),
         'description': u'boo',
         'event_id': None,
         'id': 2,
         'keywords': u'oo',
         'layout_id': 2,
         'parent_id': None,
         'site_id': None,
         'structure': structure,
         'title': u'fofoo',
         'updated_at': datetime(2012, 2, 14, 15, 13, 26, 438156),
         'url': 'sample_page',
         'version': None}
    return Page.from_dict(D)

def _getLayout():
    from altaircms.layout.models import Layout
    D = {'blocks': '[["content"],["footer"], ["js_prerender"], ["js_postrender"]]',
         'client_id': None,
         'created_at': datetime(2012, 2, 16, 11, 26, 55, 755523),
         'id': 2,
         'site_id': None,
         'template_filename': u'layout.mako',
         'title': 'simple',
         'updated_at': datetime(2012, 2, 16, 11, 26, 55, 755641)}
    return Layout.from_dict(D)
