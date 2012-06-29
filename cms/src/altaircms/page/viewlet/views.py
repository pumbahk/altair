# -*- coding:utf-8 -*-
from pyramid.view import view_config
from . import api
from markupsafe import Markup

def table_headers(headers):
    return Markup(u"<th>%s</th>" % u"</th></th>".join(headers)) 

@view_config(name="tag_from_event", renderer="altaircms:templates/event/viewlet/tags.mako")
def describe_tag(request):
    event = api.get_event(request)
    return {
        "headers": table_headers([u"タグの種類",u"",u"タグの種類",u"作成日時",u"更新日時"]), 
        "event": event, 
        "tags": event.tags
        }
