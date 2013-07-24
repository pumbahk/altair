# -*- coding:utf-8 -*-

import base64
from webhelpers.html.builder import literal
from altair.app.ticketing.core.api import get_channel
from . import api

def checkout_form(request, cart):
    if request.is_mobile:
        action = request.registry.settings.get('altair_checkout.mobile_checkin_url')
        submit = u'<input type="submit" value="楽天 お支払い" />'
    else:
        action = request.registry.settings.get('altair_checkout.checkin_url')
        submit = ''

    # checkoutをXMLに変換
    channel = get_channel(cart.channel)
    service = api.get_checkout_service(request, cart.performance.event.organization, channel)
    xml = service.create_checkout_request_xml(cart)

    # 署名作成する
    sig = api.sign_to_xml(request, cart.performance.event.organization, channel, xml)

    return literal(
        '<form id="checkout-form" action="%(action)s" method="post" accept-charset="utf-8">'
        '<input type="hidden" name="checkout" value="%(checkout)s" />'
        '<input type="hidden" name="sig" value="%(sig)s" />'
        '%(submit)s'
        '</form>' %
        dict(
            action=action,
            checkout=base64.b64encode(xml),
            sig=sig,
            submit=submit
        )
    )
