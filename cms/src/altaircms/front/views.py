# coding: utf-8
from datetime import datetime
from altaircms.page.models import Page
from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError
from altaircms.lib.fanstatic_decorator import with_jquery
from pyramid.view import view_config



def _append_preview_message(response, message, color="red", backgroundcolor="#faa"):
    preview_message = u"""
<script type="text/javascript">
  $(function(){
    var css_opt = {"text-align": "left",  "color": "%s", "font-size": "30px", "background-color": "%s"};
    $("body").prepend($("<div class='cms-message'>").css(css_opt).html("%s"));
  })
</script>
</body>
    """ % (color, backgroundcolor, message)
    response.text = response.text.replace("</body>", preview_message)    
    return response

@view_config(route_name="preview_page", decorator=with_jquery)
def preview_page(context, request):
    control = context.access_control()
    access_key = request.params.get("access_key")
    page_id = request.matchdict["page_id"]
    page = control.fetch_page_from_pageid(page_id, access_key=access_key)

    if not control.can_access():
        return HTTPForbidden(control.error_message)
    
    template = context.frontpage_template(page)
    if not control.can_rendering(template, page):
        raise HTTPInternalServerError(control.error_message)

    renderer = context.frontpage_renderer()
    response = renderer.render(template, page)

    ## ugly
    return _append_preview_message(response, u"これはpreview画面です。")


@view_config(route_name="preview_pageset", decorator=with_jquery)
def preview_pageset(context, request, published=True):
    control = context.access_control()
    pageset_id = request.matchdict["pageset_id"]
    page = control.fetch_page_from_pagesetid(pageset_id, published=published)

    if not control.can_access():
        if not published:
            raise HTTPForbidden(control.error_message)
        else:
            return preview_pageset(context, request, published=False)

    template = context.frontpage_template(page)
    if not control.can_rendering(template, page):
        raise HTTPInternalServerError(control.error_message)

    renderer = context.frontpage_renderer()
    response = renderer.render(template, page)
    ## ugly
    if published:
        return _append_preview_message(response, u"<p>これはpreview画面です。</p>", color="yellow", backgroundcolor="#ffa")
    else:
        now = datetime.now()
        messages = [u'<div>'
                    u'<p>これはpreview画面です。(注意：ページが全て非公開あるいは掲載期限を過ぎています)</p>', 
                    u'<ul><li>%s</li></ul>' % u'</li><li>'.join(u'ページ名=%s(公開ステータス: %s)' % (p.name, p.publish_status(now))for p in Page.query.filter_by(pageset_id=pageset_id).all()), 
                    u"</div>"]
        return _append_preview_message(response, u"".join(messages), color="red", backgroundcolor="#faa")


