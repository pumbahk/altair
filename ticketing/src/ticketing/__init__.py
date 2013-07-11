# -*- coding: utf-8 -*-
from altair.logicaldeleting import install as install_ld
install_ld()

import re
import json
import transaction
from sqlalchemy import engine_from_config
from pyramid.config import Configurator
from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_beaker import session_factory_from_settings
from pyramid.tweens import EXCVIEW
from pyramid.interfaces import IDict
from pyramid_beaker import set_cache_regions_from_settings

import sqlahelper

authn_exemption = re.compile(r'^(/_deform)|(/static)|(/_debug_toolbar)|(/favicon.ico)')

def setup_mailtraverser(config):
    from ticketing.mails.traverser import EmailInfoTraverser
    reg = config.registry
    traverser = EmailInfoTraverser()
    reg.registerUtility(traverser, name="lots")

def newRootFactory(klass):
    from .resources import ExemptionResource
    def root_factory(request): 
        if authn_exemption.match(request.path):
            return ExemptionResource()
        else:
            return klass(request)
    return root_factory

def exclude_js(path):
    return path.endswith(".js")

def register_globals(event):
    from .helpers import Namespace as Namespace_HH
    from .loyalty import helpers as lh
    from altair.viewhelpers import Namespace as Namespace_vh
    event.update(
        HH=Namespace_HH(event['request']),
        lh=lh,
        vh=Namespace_vh(event['request'])
        )


def main(global_config, **local_config):
    """ This function returns a Pyramid WSGI application.
    """

    with transaction.manager:
        settings = dict(global_config)
        settings.update(local_config)
    
        from .resources import TicketingAdminResource, groupfinder
        from .authentication import CombinedAuthenticationPolicy, APIAuthenticationPolicy
        from .authentication.apikey.impl import newDBAPIKeyEntryResolver
        from sqlalchemy.pool import NullPool

        engine = engine_from_config(settings, poolclass=NullPool,
                                    isolation_level='READ COMMITTED',
                                    pool_recycle=60)
        sqlahelper.add_engine(engine)

        session_factory = session_factory_from_settings(settings)
        set_cache_regions_from_settings(settings) 
        config = Configurator(settings=settings,
                              root_factory=newRootFactory(TicketingAdminResource),
                              session_factory=session_factory)
    
        config.set_authentication_policy(
            CombinedAuthenticationPolicy([
                AuthTktAuthenticationPolicy(
                    'secretstring',
                    cookie_name='backendtkt',
                    callback=groupfinder),
                APIAuthenticationPolicy(
                    resolver_factory=newDBAPIKeyEntryResolver,
                    header_name='X-Altair-Authorization',
                    userid_prefix='__altair_ticketing__api__',
                    principals=['api'])
                ])
            )
        config.set_authorization_policy(ACLAuthorizationPolicy())
    
        # multicheckout
        domain_candidates = json.loads(config.registry.settings["altair.cart.domain.mapping"])
        config.registry.utilities.register([], IDict, "altair.cart.domain.mapping", domain_candidates)
    
        config.add_static_view('static', 'ticketing:static', cache_max_age=3600)
    
        config.add_view('pyramid.view.append_slash_notfound_view',
                        context='pyramid.httpexceptions.HTTPNotFound')
    
        config.include("pyramid_fanstatic")
    
        config.add_route("index", "/")
    
        config.include('altair.browserid')
        config.include('altair.exclog')
        config.include('altair.mobile')
        config.include('altair.sqlahelper')
        config.include('altair.now')

        ### s3 assets
        config.include('altair.pyramid_assets')
        config.include('altair.pyramid_boto')
        config.include('altair.pyramid_boto.s3.assets')

        config.include('ticketing.core')
        config.include('ticketing.mails')
        config.include('ticketing.multicheckout')
        config.include('ticketing.checkout')
        config.include('ticketing.operators' , route_prefix='/operators')
        config.include('ticketing.login' , route_prefix='/login')
        config.include('ticketing.organizations' , route_prefix='/organizations')
        config.include('ticketing.api' , route_prefix='/api')
        config.include('ticketing.admin' , route_prefix='/admin')
        config.include('ticketing.events' , route_prefix='/events')
        config.include('ticketing.orders' , route_prefix='/orders')
        config.include('ticketing.master' , route_prefix='/master')
        config.include('ticketing.tickets' , route_prefix='/tickets')
        config.include('ticketing.products' , route_prefix='/products')
        config.include('ticketing.mailmags' , route_prefix='/mailmags')
        config.include('ticketing.venues' , route_prefix='/venues')
        config.include('ticketing.dashboard' , route_prefix='/dashboard')
        config.include('ticketing.bookmark' , route_prefix='/bookmark')
        config.include('ticketing.accounts' , route_prefix='/accounts')
        config.include('ticketing.payment_methods' , route_prefix='/payment_methods')
        config.include('ticketing.delivery_methods' , route_prefix='/delivery_methods')
        config.include("ticketing.qr")
        config.include("ticketing.members", route_prefix='/members')
        config.include("ticketing.memberships", route_prefix="/memberships")
        config.include('ticketing.loyalty', route_prefix='/loyalty')
        config.include('ticketing.payments')
        config.include('ticketing.payments.plugins')
        config.include('ticketing.pkginfo')
        config.include('ticketing.lots.authcancel')
        config.include('ticketing.booster.setup_order_product_attribute_metadata')
        config.include('ticketing.booster.89ers.setup_order_product_attribute_metadata')
        config.include('ticketing.booster.bambitious.setup_order_product_attribute_metadata')
        config.include('ticketing.booster.bigbulls.setup_order_product_attribute_metadata')
        config.include('ticketing.lots_admin')

        config.include("ticketing.carturl")

        ## TBA
        config.add_route("qr.make", "___________") ##xxx:
        config.include(config.maybe_dotted("ticketing.cart.import_mail_module"))
        # 上からscanされてしまうためしかたなく追加。scanをinclude先に移動させて、このincludeを削除する。
        #config.include('ticketing.cart' , route_prefix='/cart')
    
        config.add_renderer('.html' , 'pyramid.mako_templating.renderer_factory')
        config.add_renderer('.txt' , 'pyramid.mako_templating.renderer_factory')
        config.add_renderer('json'  , 'ticketing.renderers.json_renderer_factory')
        config.add_renderer('csv'   , 'ticketing.renderers.csv_renderer_factory')
        config.add_renderer('lxml'  , 'ticketing.renderers.lxml_renderer_factory')
    
        config.add_tween('.tweens.session_cleaner_factory', over=EXCVIEW)
        #config.scan('ticketing') # Bad Code

        ## cmsとの通信
        from .api.impl import CMSCommunicationApi
        event_push_communication = CMSCommunicationApi(
            settings["altaircms.event.notification_url"], 
            settings["altaircms.apikey"]
            )
        event_push_communication.bind_instance(config)
        config.include('altair.pyramid_assets')
        config.include('altair.pyramid_boto')

        config.add_subscriber(register_globals, 'pyramid.events.BeforeRender')

        config.scan(".views")
    
        return config.make_wsgi_app()
