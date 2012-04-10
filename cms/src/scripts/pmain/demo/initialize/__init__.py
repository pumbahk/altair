# -*- coding:utf-8 -*-

from contextlib import contextmanager
from altaircms.models import DBSession

def append_to_json_structure(page, key, data):
    import json
    structure = json.loads(page.structure)
    if structure.get(key) is None:
        structure[key] = []
    structure[key].append(data)
    page.structure = json.dumps(structure)
    return page

@contextmanager
def block(message):
    yield

def init():
    with block("create layout model"):
        from altaircms.layout.models import Layout
        layout0 = Layout()
        layout0.id = 1
        layout0.title = "original"
        layout0.template_filename = "original5.mako"
        layout0.blocks = '[["page_main_title"],["page_main_image","page_main_description"],["page_main_main"],["page_main_footer"]]'
        layout0.site_id = 1 ##
        layout0.client_id = 1 ##
        DBSession.add(layout0)

        layout_gallery = Layout()
        layout_gallery.id = 2
        layout_gallery.title = "original_gallery"
        layout_gallery.template_filename = "original5_gallery.mako"
        layout_gallery.blocks = '[["page_header_content"],["notice"],["page_main_header"],["page_main_title"],["page_main_main"],["page_main_footer"]]'
        layout_gallery.site_id = 1 ##
        layout_gallery.client_id = 1 ##
        DBSession.add(layout_gallery)

        layout2 = Layout()
        layout2.id = 3
        layout2.title = "original"
        layout2.template_filename = "original5.1.mako"
        layout2.blocks = '[["page_header_content"],["notice"],["page_main_header"],["page_main_title"],["page_main_image"],["page_main_description"],["page_main_main"],["page_main_footer"]]'
        layout2.site_id = 1 ##
        layout2.client_id = 1 ##
        DBSession.add(layout2)

        ## simple
        layout_col2 = Layout()
        layout_col2.title = "col2"
        layout_col2.template_filename = "col2.mako"
        layout_col2.blocks = '[["header"],["left", "right"],["footer"]]'
        layout_col2.site_id = 1 ##
        layout_col2.client_id = 1 ##
        DBSession.add(layout_col2)

        layout_col3 = Layout()
        layout_col3.title = "col3"
        layout_col3.template_filename = "col3.mako"
        layout_col3.blocks = '[["header"],["left1", "right1"],["left2", "center", "right2"], ["footer"]]'
        layout_col3.site_id = 1 ##
        layout_col3.client_id = 1 ##
        DBSession.add(layout_col3)

    from . import demo1
    demo1.init()
    from . import demo1_tab
    demo1_tab.init()
    from . import demo2
    demo2.init()
