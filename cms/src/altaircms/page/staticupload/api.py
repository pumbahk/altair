import os
from pyramid.exceptions import ConfigurationError
from pyramid.response import FileResponse
from pyramid.renderers import render_to_response

import logging
logger = logging.getLogger(__name__)

from ...interfaces import IDirectoryResourceFactory
from .. import StaticPageNotFound
from .fetcher import has_renderer
from .directory_resources import StaticPageDirectoryFactory
from .creation import get_staticupload_filesession

def get_static_page_utility(request):
    return request.registry.getUtility(IDirectoryResourceFactory, "static_page")(request=request)

def set_static_page_utility(config, factory):
    directory_validate(factory.basedir, factory.tmpdir)
    if hasattr(factory, "setup"):
        factory.setup(config)
    return config.registry.registerUtility(factory, IDirectoryResourceFactory, "static_page")

def directory_validate(basedir, tmpdir):
    if not os.path.exists(basedir):
        os.makedirs(basedir)
    else:
        if not os.path.isdir(basedir):
            raise ConfigurationError("altaircms.page.static.directory: %s is not directory" % basedir)
        if not os.access(basedir, os.W_OK):
            raise ConfigurationError("altaircms.page.static.directory: %s is not writable" % tmpdir)

    if not os.access(tmpdir, os.W_OK):
        raise ConfigurationError("altaircms.page.tmp.directory: %s is not writable" % tmpdir)
    return True

from .fetcher import CACHE_MAX_AGE
from .fetcher import ResponseMaker
from .interfaces import IStaticPageDataFetcherFactory

def get_static_page_fetcher(request, static_page):
    static_page_utility = get_static_page_utility(request)
    k = "network" if static_page.uploaded_at else "filesystem"
    factory = request.registry.queryUtility(IStaticPageDataFetcherFactory, name=k)
    return factory(request, static_page, static_page_utility)

def as_static_page_response(request, static_page, url, force_original=False, path=None, cache_max_age=CACHE_MAX_AGE):
    data = get_static_page_fetcher(request, static_page).fetch(url, path)
    response_maker = ResponseMaker(request, static_page, force_original=force_original, cache_max_age=cache_max_age)
    return response_maker.make_response(data)

