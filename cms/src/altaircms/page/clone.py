# -*- coding:utf-8 -*-
import json

from . import models
import altaircms.widget.tree.clone as wclone
from altaircms.widget.tree.proxy import WidgetTreeProxy

def page_clone(request, page, session=None):
    """ pageとwidgetlayoutをコピー
    """
    params = page.to_dict()
    params["title"] = u"%s(コピー)" % page.title
    params["url"] = page.url  # xxx?
    del params["id"]
    del params["widgets"]
    new_page = models.Page.from_dict(params)

    if session:
        session.add(new_page)
        session.flush()
    wtree = WidgetTreeProxy(page)
    new_wtree = wclone.clone(session, new_page, wtree)
    if session:
        session.flush()
    new_structure = wclone.to_structure(new_wtree)

    new_page.structure = json.dumps(new_structure)
    return new_page
