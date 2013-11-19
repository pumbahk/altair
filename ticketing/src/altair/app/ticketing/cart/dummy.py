# -*- coding:utf-8 -*-
from altair.app.ticketing.cart.selectable_renderer import selectable_renderer
from altair.app.ticketing.core.api import get_organization
from altair.app.ticketing.mailmags import models as mailmag_models
from pyramid.response import Response
from functools import wraps
import logging
logger = logging.getLogger()
from mako.template import Template

def includeme(config):
    config.add_route("dummy.cart.index", "/dummy")
    config.add_view(index_view, route_name="dummy.cart.index")
    config.add_route("dummy.cart.payment", "/dummy/payment")
    config.add_view(payment_view, route_name='dummy.cart.payment', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/pc/payment.html"))
    config.add_view(payment_view, route_name='dummy.cart.payment', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/mobile/payment.html"))

    config.add_route("dummy.payment.confirm", "/dummy/confirm")
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/pc/confirm.html"))
    config.add_view(confirm_view, route_name='dummy.payment.confirm', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/mobile/confirm.html"))

    config.add_route("dummy.payment.complete", "/dummy/complete")
    config.add_view(complete_view, route_name='dummy.payment.complete', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/pc/completion.html"))
    config.add_view(complete_view, route_name='dummy.payment.complete', request_type='altair.mobile.interfaces.IMobileRequest', request_method="GET", decorator=overwrite_validation, renderer=selectable_renderer("%(membership)s/mobile/completion.html"))

    config.add_route("dummy.timeout", "/dummy/timeout")
    config.add_view(timeout_view, route_name="dummy.timeout", decorator=overwrite_validation, renderer=selectable_renderer("altair.app.ticketing.cart:templates/%(membership)s/pc/timeout.html"))
    config.add_route("dummy.notfound", "/dummy/notfound")
    config.add_view(notfound_view, route_name="dummy.notfound", decorator=overwrite_validation, renderer=selectable_renderer("altair.app.ticketing.cart:templates/%(membership)s/pc/errors/notfound.html"))
    config.add_view(notfound_view, route_name="dummy.notfound", request_type='altair.mobile.interfaces.IMobileRequest', decorator=overwrite_validation, renderer=selectable_renderer("altair.app.ticketing.cart:templates/%(membership)s/mobile/errors/notfound.html"))

def overwrite_validation(fn):
    from altair.app.ticketing.core.models import Organization
    @wraps(fn)
    def wrapped(context, request):
        if "organization_id" in request.params:
            organization_id = request.params["organization_id"]
            logger.info("* dummy overwrite organization: organization_id = {0}".format(organization_id))
            organization = Organization.query.filter_by(id=organization_id).first()
            if organization:
                request.organization = organization
        return fn(context, request)
    return wrapped


def index_view(context, request):
    from altair.app.ticketing.core.models import Organization, Host
    links = [("dummy.cart.payment", u"支払方法選択画面"), 
             ("dummy.payment.confirm", u"注文確認画面"), 
             ("dummy.payment.complete", u"注文完了画面"), 
             ("dummy.timeout", u"タイムアウト画面"), 
             ("dummy.notfound", u"404画面")]
    template = Template(u"""
%for organization in organizations:
<h3>${organization.name}</h3>
<ul>
%for route_name, description in links:
  <li><a href="${request.route_path(route_name, _query=dict(organization_id=organization.id))}">${description}</a></li>
%endfor
</ul>
%endfor
""")
    organizations = Organization.query.filter_by(deleted_at=None).filter(Host.organization_id==Organization.id).all()
    return Response(template.render(request=request, links=links, organizations=organizations))

def _dummy_performance():
    from datetime import datetime
    class performance:
        name = "Hey"
        start_on = datetime.now()
        id = 1111
        class event:
            title = "event"
            id = 4
        class venue:
            name = "venue"
    return performance

def _dummy_order():
    import mock
    order = mock.Mock()
    order.performance = _dummy_performance()
    order.ordered_products = []
    order.transaction_fee = 100
    order.system_fee = 200
    order.delivery_fee = 300
    order.total_amount = 500
    order.payment_delivery_pair.payment_method.payment_plugin_id = 1
    order.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    return order

def _dummy_cart():
    import mock
    cart = mock.Mock()
    cart.performance = _dummy_performance()
    cart.items = []
    cart.transaction_fee = 100
    cart.system_fee = 200
    cart.delivery_fee = 300
    cart.total_amount = 500
    cart.payment_delivery_pair.payment_method.payment_plugin_id = 1
    cart.payment_delivery_pair.delivery_method.delivery_plugin_id = 1
    return cart


def _get_mailmagazines_from_organization(organization):
    return mailmag_models.MailMagazine.query.outerjoin(mailmag_models.MailSubscription) \
            .filter(mailmag_models.MailMagazine.organization==organization)
           

def confirm_view(context, request):
    import mock
    from collections import defaultdict
    with mock.patch("altair.rakuten_auth.api.authenticated_user"):
        form = mock.Mock()
        cart = _dummy_cart()
        request.session["order"] = defaultdict(str)
        magazines = _get_mailmagazines_from_organization(get_organization(request))
        user = mock.Mock()
        return dict(cart=cart, mailmagazines=magazines, user=user, form=form)


def complete_view(context, request):
    import mock
    with mock.patch("altair.rakuten_auth.api.authenticated_user"):
        order = _dummy_order()
        return dict(order=order)

def payment_view(context, request):
    import mock
    from .schemas import ClientForm
    request.session.flash(u"お支払い方法／受け取り方法をどれかひとつお選びください")
    with mock.patch("altair.rakuten_auth.api.authenticated_user"):
        params=dict(form=ClientForm(), 
                    payment_delivery_methods=[], 
                    user=mock.Mock(), 
                    user_profile=mock.Mock())
        return params
    
def timeout_view(context, request):
    return {}

def notfound_view(context, request):
    return {}
