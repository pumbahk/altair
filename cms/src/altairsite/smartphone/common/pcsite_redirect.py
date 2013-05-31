# -*- coding:utf-8 -*-

from markupsafe import Markup
from altairsite import PC_ACCESS_COOKIE_NAME

def pcsite_redirect_script(request, next="/", cookie_name=PC_ACCESS_COOKIE_NAME):
    fmt = u'''
    if(document.cookie.indexOf("%s") > -1){
        var e = $("<a>").text("SPサイトへ").attr("href", "%s");
        $("body").append(e);
     }
'''
    content = fmt % (cookie_name, request.route_path("smartphone.goto_sp_page", _query=(dict(next="/"))))
    return Markup(content)
