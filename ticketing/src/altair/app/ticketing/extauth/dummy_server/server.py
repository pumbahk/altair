# encoding: utf-8

import logging
from pyramid.decorator import reify
logger = logging.getLogger(__name__)

def setup_routes(config):
    config.add_route('eagles_extauth.user_profile', '/user/profile')

def setup_renderers(config):
    config.include('pyramid_mako')
    from altair.pyramid_extra_renderers.json import JSON
    config.add_renderer('json', JSON())

def setup_sqlalchemy(config):
    import sqlalchemy
    import sqlalchemy.orm
    from .models import Base
    config.registry.sa_engine = sqlalchemy.engine_from_config(config.registry.settings)
    config.registry.sa_base = Base
    config.registry.sa_base.metadata.create_all(config.registry.sa_engine)
    config.registry.sa_session_maker = sqlalchemy.orm.sessionmaker(bind=config.registry.sa_engine)

    def get_sa_session(request):
        retval = request.registry.sa_session_maker()
        def cleanup(request):
            try:
                if request.exception is not None:
                    request.sa_session.rollback()
                else:
                    request.sa_session.commit()
            finally:
                request.sa_session.close()
        request.add_finished_callback(cleanup)
        return retval
    config.set_request_property(get_sa_session, 'sa_session', reify=True)

def setup_request_properties(config):
    from datetime import datetime
    config.set_request_property(lambda request: datetime.now(), 'now', reify=True)

def main():
    return paster_main({})

def paster_main(global_config, **local_config):
    from pyramid.config import Configurator
    settings = dict(global_config)
    settings.update(local_config)
    settings['mako.directories'] = 'altair.app.ticketing.extauth.dummy_server:templates'
    config = Configurator(settings=settings)
    config.scan('.views')
    config.include("pyramid_fanstatic")
    config.include('altair.exclog')
    config.include(setup_sqlalchemy)
    config.include(setup_renderers)
    config.include(setup_routes)
    config.include(setup_request_properties)
    return config.make_wsgi_app()
