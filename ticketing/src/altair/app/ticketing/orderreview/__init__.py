# -*- coding:utf-8 -*-
import json
from pyramid.config import Configurator
from pyramid.httpexceptions import HTTPNotFound, HTTPFound
from pyramid.exceptions import PredicateMismatch
from pyramid.authorization import ACLAuthorizationPolicy
from sqlalchemy import engine_from_config
from sqlalchemy.pool import NullPool
import sqlahelper
from altair.app.ticketing.cart.rendering import selectable_renderer

from altair.app.ticketing.i18n import custom_locale_negotiator

class RakutenAuthContext(object):
    def __init__(self, request):
        self.request = request

def decide_auth_types(request, classification):
    if hasattr(request, 'context') and isinstance(request.context, RakutenAuthContext):
        from altair.rakuten_auth import AUTH_PLUGIN_NAME
        return [AUTH_PLUGIN_NAME]
    auth_type = request.session.get('orderreview_auth_type_override')
    if auth_type is not None:
        return [auth_type]
    auth_type = request.organization.setting.cart_setting.auth_type
    if auth_type is not None:
        return [auth_type]
    return None


def setup_static_views(config):
    config.add_static_view('static', 'altair.app.ticketing.orderreview:static', cache_max_age=3600)
    config.add_static_view('static_', 'altair.app.ticketing.cart:static', cache_max_age=3600)
    config.add_static_view('img', 'altair.app.ticketing.cart:static', cache_max_age=3600)

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    settings = config.registry.settings
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"],
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
            mapping={"altair.app.ticketing.cart:static/": "/cart/static/"}))

def includeme(config):
    ## review
    config.add_route('order_review.index', '/', factory='.resources.LandingViewResource')
    config.add_route('order_review.guest', '/guest')  # old url
    config.add_route('order_review.form', '/form', factory='.resources.LandingViewResource')
    config.add_route('order_review.form2', '/show', request_method='GET', factory='.resources.LandingViewResource')
    config.add_route('order_review.edit_order_attributes.form', '/show', request_method='POST', request_param='action=edit_order_attributes.form', factory='.resources.OrderReviewResource')
    config.add_route('order_review.edit_order_attributes.update', '/show', request_method='POST', request_param='action=edit_order_attributes.update', factory='.resources.OrderReviewResource')
    config.add_route('order_review.show', '/show', request_method='POST', factory='.resources.OrderReviewResource')

    ## qr
    config.add_route('order_review.qr_print', '/qr/print', factory='.resources.QRViewResource')
    config.add_route('order_review.qr_send', '/qr/send', factory='.resources.QRViewResource')
    config.add_route('order_review.qr', '/qr/{ticket_id}/{sign}/ticket', factory='.resources.QRViewResource')
    config.add_route('order_review.qr_confirm', '/qr/{ticket_id}/{sign}/', factory='.resources.QRViewResource')
    config.add_route('order_review.qrdraw', '/qr/{ticket_id}/{sign}/image', factory='.resources.QRViewResource')

    ## orion
    config.add_route('order_review.orion_send', '/qr/eg_send', factory='.resources.EventGateViewResource')
    config.add_route('order_review.orion_draw', '/qr/eg_print/{token}/{serial}/{sign}', factory='.resources.EventGateViewResource')

    ## mypage
    config.add_route('mypage.show', '/mypage', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.mailmag.confirm', '/mypage/mailmag/confirm', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.mailmag.complete', '/mypage/mailmag/complete', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.order.show', '/mypage/order/show', factory='.resources.MyPageOrderReviewResource')
    config.add_route('mypage.logout', '/mypage/logout', factory='.resources.MyPageListViewResource')
    config.add_route('mypage.autologin', '/mypage/autologin', factory='.resources.MyPageListViewResource')

    ## word
    config.add_route('mypage.word.show', '/mypage/word/', factory='.resources.MyPageResource')
    config.add_route('mypage.word.configure', '/mypage/word/configure', factory='.resources.MyPageResource')
    config.add_route('mypage.word.search', '/mypage/word/search', factory='.resources.MyPageResource')
    config.add_route('mypage.word.subscribe', '/mypage/word/subscribe', factory='.resources.MyPageResource')
    config.add_route('mypage.word.unsubscribe', '/mypage/word/unsubscribe', factory='.resources.MyPageResource')

    ## misc
    config.add_route('contact', '/contact', factory='.resources.ContactViewResource')
    config.add_route('order_review.information', '/information')  # refs 10883

def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.fc_auth')
    config.include('altair.app.ticketing.extauth.userside_impl')
    config.add_route('rakuten_auth.verify', '/verify', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.verify2', '/verify2', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.error', '/error', factory=RakutenAuthContext)
    config.set_who_api_decider(decide_auth_types)
    from altair.auth import set_auth_policy
    from altair.app.ticketing.security import AuthModelCallback
    from pyramid.security import forget
    set_auth_policy(config, AuthModelCallback(config))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    def forbidden_handler(context, request):
        forget(request)
        return HTTPFound(request.route_path('order_review.index'))
    config.set_forbidden_handler(forbidden_handler)

def setup_cms_communication_api(config):
    import altair.app.ticketing.api.impl as api_impl
    api_impl.bind_communication_api(config,
                            "..api.impl.CMSCommunicationApi",
                            config.registry.settings["altair.cms.api_url"],
                            config.registry.settings["altair.cms.api_key"]
                            )

def main(global_config, **local_config):
    settings = dict(global_config)
    settings.update(local_config)

    engine = engine_from_config(settings, poolclass=NullPool)
    sqlahelper.add_engine(engine)

    config = Configurator(
        settings=settings,
        root_factory='.resources.DefaultResource'
        )
    config.include('altair.app.ticketing.setup_beaker_cache')

    config.include('pyramid_layout')
    config.include('pyramid_dogpile_cache')

    ### include altair.*
    config.include('altair.browserid')
    config.include('altair.exclog')
    config.include('altair.httpsession.pyramid')
    config.include('altair.mq')
    config.include('altair.pyramid_dynamic_renderer')
    config.include('altair.sqlahelper')

    config.include('altair.app.ticketing.cart')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_payment_delivery_plugins')
    config.include('altair.app.ticketing.cart.setup_mobile')
    config.include('altair.app.ticketing.cart.setup_cart_interface')
    config.include('altair.app.ticketing.cart.import_mail_module')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')
    config.include(setup_auth)

    config.add_subscriber('.subscribers.add_helpers', 'pyramid.events.BeforeRender')
    config.add_subscriber('altair.app.ticketing.i18n.add_renderer_globals', 'pyramid.events.BeforeRender')
    config.add_subscriber('.i18n.add_localizer', 'pyramid.events.NewRequest')
    config.add_translation_dirs('altair.app.ticketing:locale')
    config.set_locale_negotiator(custom_locale_negotiator)

    config.include(setup_static_views)
    config.include('.')
    config.include('.view_context')
    config.include('.preview')
    config.scan(".views")
    config.scan(".panels")

    setup_cms_communication_api(config)

    return config.make_wsgi_app()

