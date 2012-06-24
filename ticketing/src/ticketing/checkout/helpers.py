# -*- coding:utf-8 -*-

import base64
from webhelpers.html.builder import literal
from . import api

def begin_checkout_form(request):
    action = request.registry.settings.get('altair_checkout.checkin_url')
    return literal('<form action="%(action)s" method="%(method)s" accept-charset="%(accept_charset)s">' %
                    dict(action=action, method='post', accept_charset='utf-8'))

def render_checkout(request, cart):
    # checkoutをXMLに変換
    service = api.get_checkout_service(request)
    xml = service.create_checkout_request_xml(cart)

    # 署名作成する
    sig = api.sign_to_xml(request, xml)

    return literal('<input type="hidden" name="checkout" value="%(checkout)s" />'
                   '<input type="hidden" name="sig" value="%(sig)s" />' % 
                    dict(checkout=base64.b64encode(xml), sig=sig))

def end_checkout_form(request):
    return literal('</form>')
