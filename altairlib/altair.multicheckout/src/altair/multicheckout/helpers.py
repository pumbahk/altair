# -*- coding:utf-8 -*-
from markupsafe import Markup
from mako.template import Template

acs_form_tmpl = u"""<form name='PAReqForm' method='POST' action='${secure3d_context.AcsUrl}'>
        <input type='hidden' name='PaReq' value='${secure3d_context.PaReq}'>
        <input type='hidden' name='TermUrl' value='${term_url}'>
        <input type='hidden' name='MD' value='${secure3d_context.Md}'>
        </form>
        <script type='text/javascript'>function onLoadHandler(){document.PAReqForm.submit();};window.onload = onLoadHandler; </script>
        """
acs_form_tmpl = Template(acs_form_tmpl)

def secure3d_acs_form(request, term_url, secure3d_enrol_response):
    """ 3D認証画面要求フォーム
    """

    body = acs_form_tmpl.render(secure3d_context=secure3d_enrol_response, term_url=term_url)
    return Markup(body)