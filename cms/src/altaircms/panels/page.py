# -*- coding:utf-8 -*-
import sqlalchemy.orm as orm
from altaircms.datelib import get_now
from altaircms.page import helpers
from altaircms.auth.accesskey.api import get_page_access_key_control
from altaircms.auth.models import PageAccesskey

def page_describe_panel(context, request, current_page):
    now = get_now(request)
    page_status = current_page.publish_status(now)
    return {"page": current_page, "page_status": page_status, "myhelpers": helpers}

def page_accesskey_section_panel(context, request, page):
    control = get_page_access_key_control(request, page)
    accesskeys = control.query_access_key().options(orm.joinedload(PageAccesskey.operator)).all()
    return dict(page=page, page_title=u"アクセスキー", 
                preview_with_accesskey_url_gen=lambda hashkey: request.route_url("preview_page", page_id=page.id, _query=dict(access_key=hashkey)), 
                create_accesskey_url=request.route_path("auth.accesskey.pagekey",action="create", page_id=page.id), 
                update_accesskey_url=request.route_path("auth.accesskey.detail", accesskey_id="__id__"), 
                delete_accesskey_url=request.route_path("auth.accesskey.pagekey",action="delete", page_id=page.id), 
                accesskeys=accesskeys)
