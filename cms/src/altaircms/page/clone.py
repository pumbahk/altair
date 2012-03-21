# -*- coding:utf-8 -*-
import json

from . import models
import altaircms.widget.tree.clone as wclone
from altaircms.widget.tree.proxy import WidgetTreeProxy

def page_clone(page, session=None):
    """ pageとwidgetlayoutをコピー
    """
    params = page.to_dict()
    del params["id"]
    new_page = models.Page.from_dict(params)
    if session:
        session.add(new_page)
        session.flush()
    new_wtree, new_structure = page_structure_clone(new_page, session=session)
    new_page.structure = json.dumps(new_structure)
    return new_page

def page_structure_clone(page, session=None):
    wtree = WidgetTreeProxy(page)
    new_wtree = wclone.clone(session, page, wtree)
    if session:
        session.flush()
    new_structure = wclone.to_structure(new_wtree)
    return new_wtree, new_structure
    
    
