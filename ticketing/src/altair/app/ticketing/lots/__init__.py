# -*- coding:utf-8 -*-
"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from pyramid.tweens import INGRESS
from altair.app.ticketing.wsgi import direct_static_serving_filter_factory
from ..users.models import Membership
from ..cart import setup_cms_communication_api
from altair.sqlahelper import get_db_session

import sqlalchemy as sa
import sqlahelper

from .interfaces import ILotResource

from altair.app.ticketing.i18n import custom_locale_negotiator

class RakutenAuthContext(object):
    def __init__(self, request):
        self.request = request

def decide_auth_types(request, classification):
    """ WHO API 選択
    """
    if hasattr(request, "context"):
        if ILotResource.providedBy(request.context) and request.context.lot is not None:
            return [request.context.lot.auth_type]
        elif isinstance(request.context, RakutenAuthContext):
            from altair.rakuten_auth import AUTH_PLUGIN_NAME
            return [AUTH_PLUGIN_NAME]
    else:
        return []

def register_globals(event):
    from . import helpers
    event.update(h=helpers)

def setup_routes(config):
    # 申し込みフェーズ
    config.add_route('lots.entry.agreement', 'events/{event_id}/entry/{lot_id}/agreement')
    config.add_route('lots.entry.agreement.compat', 'events/agreement/{event_id}/entry/{lot_id}')
    config.add_route('lots.index.recaptcha', 'events/{event_id}/entry/{lot_id}/recaptcha')
    config.add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    config.add_route('lots.entry.step1', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step1', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step2', 'events/{event_id}/entry/{lot_id}/options/{option_index}/step2', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step3', 'events/{event_id}/entry/{lot_id}/step3', factory='.resources.LotOptionSelectionResource')
    config.add_route('lots.entry.step4', 'events/{event_id}/entry/{lot_id}/step4')
    config.add_route('lots.entry.sp_step1', 'events/{event_id}/entry/{lot_id}/sp_step1')
    config.add_route('lots.entry.sp_step2', 'events/{event_id}/entry/{lot_id}/sp_step2')
    config.add_route('lots.entry.sp_step3', 'events/{event_id}/entry/{lot_id}/sp_step3')
    config.add_route('lots.entry.sp_step4', 'events/{event_id}/entry/{lot_id}/sp_step4')
    config.add_route('lots.entry.rsp', 'rsp', factory='.resources.LotResource')
    config.add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    config.add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')
    config.add_route('lots.entry.logout', 'events/logout', factory='.resources.LotLogoutResource')
    config.add_route('lots.review.withdraw.withdraw', 'review/withdraw/withdraw', factory='.resources.LotReviewWithdrawResource')
    config.add_route('lots.review.withdraw.confirm', 'review/withdraw/confirm', factory='.resources.LotReviewWithdrawResource')

    config.add_route('lots.review.edit_lot_entry_attributes.form', 'review', request_method='POST',request_param='action=edit_lot_entry_attributes.form', factory='.resources.LotReviewResource')
    config.add_route('lots.review.edit_lot_entry_attributes.update', 'review', request_method='POST',request_param='action=edit_lot_entry_attributes.update', factory='.resources.LotReviewResource')
    config.add_route('lots.review.index', 'review', factory='.resources.LotReviewResource')

    # 当選フェーズ
    #config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    #config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    #config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')


def setup_ticketing_auth_plugins(config):
    config.include('altair.app.ticketing.authentication')
    config.add_ticketing_auth_plugin_entrypoints('lots.entry.agreement')
    config.add_ticketing_auth_plugin_entrypoints('lots.entry.agreement.compat')
    config.add_ticketing_auth_plugin_entrypoints('lots.entry.index')


def setup_auth(config):
    config.include('altair.auth')
    config.include('altair.rakuten_auth')
    config.include('altair.app.ticketing.fc_auth')
    config.include('altair.app.ticketing.extauth.userside_impl')
    # キーワード認証＆外部会員番号取得キーワード認証
    config.include(setup_ticketing_auth_plugins)

    config.set_who_api_decider(decide_auth_types)
    from altair.auth import set_auth_policy
    from altair.app.ticketing.security import AuthModelCallback
    set_auth_policy(config, AuthModelCallback(config))
    config.set_authorization_policy(ACLAuthorizationPolicy())
    config.set_forbidden_handler(forbidden_handler)

    # 楽天認証コールバック
    config.add_route('rakuten_auth.verify', '/verify', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.verify2', '/verify2', factory=RakutenAuthContext)
    config.add_route('rakuten_auth.error', '/error', factory=RakutenAuthContext)


def forbidden_handler(context, request):
    from altair.app.ticketing.cart.view_support import render_view_to_response_with_derived_request
    # XXX: 本当は context をこういう使い方するべきではない
    session = get_db_session(request, 'slave')
    membership_name=request.altair_auth_info['membership']
    membership=session.query(Membership).filter(Membership.organization_id==request.organization.id).filter(Membership.name==membership_name).one()

    message = u'{membergroup_name} としてログインしています。<br/>' \
              u'恐れ入りますが、現在、こちらのアカウントでは {event_name} {lot_name} の受付を行っておりません。<br/>' \
              u'本受付の対象アカウントでログインしていただけますようお願いいたします。'

    locale_name = getattr(request, 'locale_name', None)
    if locale_name and locale_name != 'ja':
        message = message + u'<br/><br/>' \
                            u'You logged in as "{membergroup_name}".<br/>' \
                            u'The application for "{event_name} {lot_name}" is not available for this account.<br/>' \
                            u'Please login with a proper account.'

    request.context.message = message.format(
        lot_name=request.context.lot.name,
        event_name=request.context.lot.event.title,
        membergroup_name=request.altair_auth_info['membergroup'],
    )
    response = render_view_to_response_with_derived_request(
        context_factory=lambda _:request.context,
        request=request,
        route=('lots.entry.logout', {})
        )
    if response is not None:
        response.status = 403
    return response


class CartInterface(object):
    def get_cart(self, request, retrieve_invalidated=False):
        from .api import get_entry_cart
        return get_entry_cart(request)

    def get_success_url(self, request):
        from .urls import entry_confirm
        cart = self.get_cart(request)
        request.matchdict['lot_id'] = cart.lot.id
        request.matchdict['event_id'] = cart.sales_segment.event.id
        return entry_confirm(request)

    def get_cart_by_order_no(self, request, order_no, retrieve_invalidated=False):
        raise NotImplementedError()

    def make_order_from_cart(self, request, cart):
        raise NotImplementedError()

    def cont_complete_view(self, context, request, order_no, magazine_ids):
        raise NotImplementedError()


def setup_cart(config):
    from altair.app.ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from altair.app.ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

    config.set_cart_interface(CartInterface())


def setup_mailtraverser(config):
    from altair.app.ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

def includeme(config):
    config.include('.sendmail')
    config.include('.subscribers')
    config.include('.workers')

STATIC_URL_PREFIX = '/static/'
STATIC_URL_S3_PREFIX = '/lots/static/'
STATIC_ASSET_SPEC = 'altair.app.ticketing.lots:static/'
CART_STATIC_URL_PREFIX = '/c_static/'
CART_STATIC_S3_URL_PREFIX = '/cart/static/'
CART_STATIC_ASSET_SPEC = 'altair.app.ticketing.cart:static/'
FC_AUTH_URL_PREFIX = '/fc_auth/static/'
FC_AUTH_STATIC_ASSET_SPEC = "altair.app.ticketing.fc_auth:static/"
PAYMENT_STATIC_URL_PREFIX = '/static.payment/'
PAYMENT_CDN_URL_PREFIX = '/payments/plugins/static/'
PAYMENT_STATIC_ASSET_SPEC = 'altair.app.ticketing.payments.plugins:static/'

def main(global_config, **local_config):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    settings = dict(global_config)
    settings.update(local_config)

    from sqlalchemy.pool import NullPool
    engine = sa.engine_from_config(settings, poolclass=NullPool, isolation_level='READ COMMITTED')

    sqlahelper.add_engine(engine)

    config = Configurator(settings=settings, root_factory=".resources.lot_resource_factory")

    config.include('altair.app.ticketing.setup_beaker_cache')

    config.include('pyramid_mako')
    config.add_mako_renderer('.html')
    config.add_mako_renderer('.txt')

    ### includes altair.*
    config.include('altair.httpsession.pyramid')
    config.include('altair.browserid')
    config.include('altair.sqlahelper')
    config.include('altair.exclog')
    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')
    config.include('altair.pyramid_tz')
    config.include('altair.mobile')
    config.add_smartphone_support_predicate('altair.app.ticketing.cart.predicates.smartphone_enabled')
    config.include('altair.pyramid_dynamic_renderer')

    config.include("altair.cdnpath")
    from altair.cdnpath import S3StaticPathFactory
    config.add_cdn_static_path(S3StaticPathFactory(
            settings["s3.bucket_name"],
            exclude=config.maybe_dotted(settings.get("s3.static.exclude.function")),
            mapping={
                FC_AUTH_STATIC_ASSET_SPEC: FC_AUTH_URL_PREFIX,
                CART_STATIC_ASSET_SPEC: CART_STATIC_S3_URL_PREFIX,
                PAYMENT_STATIC_ASSET_SPEC: PAYMENT_CDN_URL_PREFIX,
                }))
    config.add_static_view(STATIC_URL_PREFIX, STATIC_ASSET_SPEC, cache_max_age=3600)
    config.add_static_view(CART_STATIC_URL_PREFIX, CART_STATIC_ASSET_SPEC, cache_max_age=3600)
    config.add_static_view(PAYMENT_STATIC_URL_PREFIX, PAYMENT_STATIC_ASSET_SPEC, cache_max_age=3600)

    config.include('altair.app.ticketing.users')
    config.include('altair.app.ticketing.multicheckout')
    config.include('altair.app.ticketing.sej')
    config.include('altair.app.ticketing.sej.userside_impl')
    config.include('altair.app.ticketing.payments')
    config.include('altair.app.ticketing.payments.plugins')
    config.include('altair.app.ticketing.mails')
    config.include('altair.app.ticketing.cart.request')
    config.include('altair.app.ticketing.cart.view_context')
    config.include('altair.app.ticketing.cart.setup__renderers')
    config.include('altair.app.ticketing.cart.setup_payment_renderers')
    config.include("altair.app.ticketing.cart.preview")
    config.include('altair.app.ticketing.cooperation.rakuten_live')

    config.include(setup_auth)
    config.include(setup_cart)
    config.include(setup_mailtraverser)
    config.include(setup_routes)

    config.include('.rendering')
    config.include('.sendmail')
    config.include('.subscribers')

    config.add_tween('altair.app.ticketing.tweens.session_cleaner_factory', under=INGRESS)

    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    config.add_subscriber('altair.app.ticketing.i18n.add_renderer_globals', 'pyramid.events.BeforeRender')
    config.add_subscriber('.i18n.add_localizer', 'pyramid.events.NewRequest')
    config.add_translation_dirs('altair.app.ticketing:locale')
    config.set_locale_negotiator(custom_locale_negotiator)

    config.scan(".views")
    config.scan(".mobile_views")
    config.scan(".smartphone_views")
    config.scan(".layouts")

    setup_cms_communication_api(config)

    import os
    import newrelic.agent
    app = config.make_wsgi_app()
    newrelic_conf_file_path = '/etc/newrelic/altair.ticketing.lots.newrelic.ini'
    if os.path.isfile(newrelic_conf_file_path):
        newrelic.agent.initialize(newrelic_conf_file_path)
        app = newrelic.agent.WSGIApplicationWrapper(app)

    return direct_static_serving_filter_factory({
        STATIC_URL_PREFIX: STATIC_ASSET_SPEC,
        CART_STATIC_URL_PREFIX: CART_STATIC_ASSET_SPEC,
        FC_AUTH_URL_PREFIX: FC_AUTH_STATIC_ASSET_SPEC,
        PAYMENT_STATIC_URL_PREFIX: PAYMENT_STATIC_ASSET_SPEC,
    })(global_config, app)

