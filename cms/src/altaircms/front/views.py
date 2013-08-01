# coding: utf-8
from altaircms.datelib import get_now
from altaircms.page.models import Page
from pyramid.httpexceptions import HTTPInternalServerError, HTTPNotFound
from altaircms.lib.fanstatic_decorator import with_jquery
from pyramid.view import view_config
from altaircms.linklib import get_usersite_url_builder
import logging 
logger = logging.getLogger(__name__)



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
        logger.warn(control.error_message)
        return HTTPInternalServerError(control.error_message)
  
    discriptor = control.frontpage_discriptor(page)
    if not discriptor.exists():
        msg = "front pc access template %s is not found" % discriptor.abspath()
        logger.warn(msg)
        raise HTTPInternalServerError(msg)

    renderer = control.frontpage_renderer()
    response = renderer.render(discriptor.absspec(), page)
    ## ugly
    now = get_now(request)
    if not page.published or (page.publish_begin and now < page.publish_begin) or (page.publish_end and now > page.publish_end):
        return _append_preview_message(response, u"これはpreview画面です ({0}) 現在時刻:{1}".format(page.publish_status(now),  now), color="red", backgroundcolor="#faa")
    else:
        return _append_preview_message(response, u"これはpreview画面です ({0}) 現在時刻:{1}".format(page.publish_status(now),  now), color="green", backgroundcolor="#afa")



@view_config(route_name="preview_pageset", decorator=with_jquery)
def preview_pageset(context, request, published=True):
    control = context.access_control()
    pageset_id = request.matchdict["pageset_id"]
    page = control.fetch_page_from_pagesetid(pageset_id, published=published)

    if not control.can_access():
        if not published:
            logger.warn(control.error_message)
            raise HTTPInternalServerError(control.error_message)
        else:
            return preview_pageset(context, request, published=False)

    discriptor = control.frontpage_discriptor(page)
    if not discriptor.exists():
        msg = "front pc access template %s is not found" % discriptor.abspath()
        logger.warn(msg)
        raise HTTPInternalServerError(msg)

    renderer = control.frontpage_renderer()
    response = renderer.render(discriptor.absspec(), page)
    ## ugly
    now = get_now(request)
    if published:
        usersite_url = get_usersite_url_builder(request).build(page.pageset)
        message = u"""
<div>
<p>これはpreview画面です ({status}) 現在時刻:{now} <a href='{url}'>usersiteのurl</a></p>
</div>
""".format(status=page.publish_status(now), now=now, url=usersite_url)
        return _append_preview_message(response, message.replace("\n", "\\n"), color="green", backgroundcolor="#afa")
    else:
        messages = [u'<div>'
                    u"<p>これはpreview画面です ({0}) 現在時刻:{1}</p>".format(page.publish_status(now),  now), 
                    u'<p>(注意：ページが全て非公開あるいは掲載期限を過ぎています)</p>', 
                    u'<ul><li>%s</li></ul>' % u'</li><li>'.join(u'ページ名=%s(公開ステータス: %s)' % (p.name, p.publish_status(now)) for p in Page.query.filter_by(pageset_id=pageset_id).all()), 
                    u"</div>"]
        return _append_preview_message(response, u"".join(messages), color="red", backgroundcolor="#faa")


@view_config(route_name="preview_pageset", context=HTTPInternalServerError, 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             renderer="altaircms:templates/front/rendering_error.html")
@view_config(route_name="preview_page", context=HTTPInternalServerError, 
             decorator="altaircms.lib.fanstatic_decorator.with_bootstrap", 
             renderer="altaircms:templates/front/rendering_error.html")
def invalid_page_view(context, request):
    if not getattr(request, "organization", None):
        raise HTTPNotFound()
    return {"message": context.message}
