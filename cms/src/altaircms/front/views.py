# coding: utf-8

from pyramid.httpexceptions import HTTPForbidden
from pyramid.httpexceptions import HTTPInternalServerError
from altaircms.lib.fanstatic_decorator import with_jquery
from pyramid.view import view_config



def _append_preview_message(response, message):
    preview_message = u"""
<script type="text/javascript">
  $(function(){
    var css_opt = {"text-align": "left",  "color": "red", "font-size": "45px"};
    $("body").prepend($("<div class='cms-message'>").css(css_opt).text("%s"));
  })
</script>
</body>
    """ % message
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
def preview_pageset(context, request):
    control = context.access_control()
    pageset_id = request.matchdict["pageset_id"]
    page = control.fetch_page_from_pagesetid(pageset_id)

    if not control.can_access():
        return HTTPForbidden(control.error_message)
    
    template = context.frontpage_template(page)
    if not control.can_rendering(template, page):
        raise HTTPInternalServerError(control.error_message)

    renderer = context.frontpage_renderer()
    response = renderer.render(template, page)
    ## ugly
    return _append_preview_message(response, u"これはpreview画面です。")


