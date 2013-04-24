# -*- coding:utf-8 -*-

"""
"""
import json
from pyramid.config import Configurator
from pyramid.interfaces import IRequest, IDict
from pyramid_beaker import session_factory_from_settings
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.tweens import EXCVIEW
from pyramid_selectable_renderer import SelectableRendererSetup
from pyramid_selectable_renderer.custom import RecieveTemplatePathFormat, RecieveTemplatePathCandidatesDict, SelectByRequestGen
from ticketing.core.api import get_organization

import sqlalchemy as sa
import sqlahelper

class WhoDecider(object):
    def __init__(self, request):
        self.request = request

    def decide(self):
        """ WHO API 選択
        """
        #return self.request.organization.setting.auth_type
        return get_organization(self.request).setting.auth_type

def register_globals(event):
    from . import helpers
    event.update(h=helpers)


@SelectByRequestGen.generate
def get_template_path_args(request):
    try:
        return dict(membership=get_organization(request).short_name)
    except:
        return dict(membership="__default__")

selectable_renderer = SelectableRendererSetup(
    RecieveTemplatePathFormat,
    get_template_path_args,
    renderer_name="selectable_renderer"
    )

def includeme(config):
    config.include(setup_cart)
    config.include(setup_mailtraverser)
    config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')
    config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
    config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
    selectable_renderer.register_to(config)

    # 申し込みフェーズ
    config.add_route('lots.entry.index', 'events/{event_id}/entry/{lot_id}')
    config.add_route('lots.entry.confirm', 'events/{event_id}/entry/{lot_id}/confirm')
    config.add_route('lots.entry.completion', 'events/{event_id}/entry/{lot_id}/completion')

    # 申し込み確認
    config.add_route('lots.review.index', 'review')

    # 当選フェーズ
    config.add_route('lots.payment.index', 'events/{event_id}/payment/{lot_id}')
    config.add_route('lots.payment.confirm', 'events/{event_id}/payment/{lot_id}/confirm')
    config.add_route('lots.payment.completion', 'events/{event_id}/payment/{lot_id}/completion')
  
    # 楽天認証コールバック
    config.add_route('rakuten_auth.login', '/login')
    config.add_route('rakuten_auth.verify', '/verify')
    config.add_route('rakuten_auth.verify2', '/verify2')
    config.add_route('rakuten_auth.error', '/error')

    config.scan(".")

# TODO: carts.includemeに移動
def setup_cart(config):

    from ticketing.cart.interfaces import IStocker, IReserving, ICartFactory
    from ticketing.cart.stocker import Stocker
    reg = config.registry
    reg.adapters.register([IRequest], IStocker, "", Stocker)

    from ticketing.payments.interfaces import IGetCart
    cart_getter = config.maybe_dotted(".api.get_entry_cart")
    reg.registerUtility(cart_getter, IGetCart)


def setup_mailtraverser(config):
    from ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

def main(global_config, **local_config):
    """ ひとまず機能実装のため(本番も別インスタンスにするか未定) """
    settings = dict(global_config)
    settings.update(local_config)

    engine = sa.engine_from_config(settings)
    sqlahelper.add_engine(engine)
    session_factory = session_factory_from_settings(settings)

    config = Configurator(settings=settings,
                          root_factory=".resources.LotResource")
    config.set_session_factory(session_factory)
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_static_view('c_static', 'ticketing.cart:static', cache_max_age=3600)

    config.include(".")

    ### includes altair.*
    config.include('altair.auth')
    config.include('altair.browserid')
    config.include('altair.exclog')

    config.include('altair.mobile')

    config.include('ticketing.rakuten_auth')
    config.include("ticketing.payments")
    config.include("ticketing.payments.plugins")
    config.add_tween('ticketing.tweens.session_cleaner_factory', over=EXCVIEW)

    config.include('altair.pyramid_assets')
    config.include('altair.pyramid_boto')

    config.set_authorization_policy(ACLAuthorizationPolicy())
    return config.make_wsgi_app()
