import os
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IRendererFactory
from pyramid.response import FileResponse
from pyramid.renderers import render_to_response

import logging
logger = logging.getLogger(__name__)

from ...interfaces import IDirectoryResourceFactory
from .. import StaticPageNotFound
from altairsite.front.api import get_frontpage_discriptor_resolver
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

def has_renderer(request, path):
    ext = os.path.splitext(path)[1]
    return bool(request.registry.queryUtility(IRendererFactory, name=ext))

CACHE_MAX_AGE=60
def as_wrapped_resource_response(request, static_page, fullpath, body_var_name="inner_body", cache_max_age=CACHE_MAX_AGE):
    if not (static_page.layout_id and has_renderer(request, fullpath)):
        return FileResponse(fullpath, request=request, cache_max_age=cache_max_age)
    resolver = get_frontpage_discriptor_resolver(request)
    discriptor = resolver.resolve(request, static_page.layout, verbose=True)
    if not discriptor.exists():
        return FileResponse(fullpath, request=request, cache_max_age=cache_max_age)
    try:
        params = {body_var_name: open(fullpath).read().decode("utf-8"), 
                  "static_page": static_page} #ok?
    except (IOError, OSError):
        raise
    except Exception, e:
        logger.exception(str(e))
        params = {body_var_name: ""}
    return render_to_response(discriptor.absspec(), params, request)

def as_static_page_response(request, static_page, url, force_original=False, path=None, cache_max_age=CACHE_MAX_AGE):
    # if static_page.uploaded_at:
    #     return _static_page_response_network(request, static_page, url, force_original=force_original, path=path, cache_max_age=cache_max_age)
    # else:
    return _static_page_response_filesystem(request, static_page, url, force_original=force_original, path=path, cache_max_age=cache_max_age)

def _static_page_response_filesystem(request, static_page, url, force_original=False, path=None, cache_max_age=CACHE_MAX_AGE):
    if path is None:
        static_page_utility = get_static_page_utility(request)
        if url.startswith("/"):
            url_parts = url[1:]
        else:
            url_parts = url
        url_parts = "/".join(url_parts.split("/")[1:]) #foo/bar -> bar
        path = os.path.join(static_page_utility.get_rootname(static_page), url_parts)
    try:
        if force_original:
            return FileResponse(path, request=request, cache_max_age=cache_max_age)
        else:
            return as_wrapped_resource_response(request, static_page, path, cache_max_age=cache_max_age)
    except (IOError, OSError):
        msg = "%s is not found" % path
        logger.info(msg)
        raise StaticPageNotFound(msg)
    except Exception as e:
        logger.exception(e)
        raise StaticPageNotFound("exception is occured")

import urllib
from altaircms.response import FileLikeResponse
def _static_page_response_network(request, static_page, url, force_original=False, path=None, cache_max_age=CACHE_MAX_AGE):
    static_page_utility = get_static_page_utility(request)
    if path:     
        io = urllib.urlopen(static_page_utility.get_url(path))
    else:
        file_path = url[1:] if url.startswith("/") else url
        prefix, file_path = file_path.split("/", 1)
        if not file_path in static_page.file_structure:
            logger.warn("{0} is not found in {1}".format(file_path, static_page.file_structure_text))
            raise StaticPageNotFound()
        url_parts = "/{0}/{1}/{2}/{3}".format(request.organization.short_name, prefix, static_page.id, file_path)
        io = urllib.urlopen(static_page_utility._get_url(url_parts))
        path = url #xxx:
    try:
        size = int(io.info().get("Content-Length", "0"))
    except ValueError:
        size = 0
    if io.getcode() != 200:
        logger.info("static page response not success: url={0}, code={1}".format(io.geturl(), io.getcode()))
        raise StaticPageNotFound()
    try:
        if force_original:
            return FileLikeResponse(io, request=request, cache_max_age=cache_max_age, 
                                    content_type=io.info().typeheader, 
                                    content_length=size, _BLOCK_SIZE=4096)
        else:
            return as_wrapped_resource_response_network(request, static_page, io, path,
                                                        cache_max_age=cache_max_age,
                                                        content_type=io.info().typeheader, 
                                                        content_length=size)
    except (IOError, OSError):
        msg = "%s is not found" % path
        logger.info(msg)
        raise StaticPageNotFound(msg)
    except Exception as e:
        logger.exception(e)
        raise StaticPageNotFound("exception is occured")

## todo: refactoring
def as_wrapped_resource_response_network(request, static_page, io, fullpath, body_var_name="inner_body",
                                         cache_max_age=CACHE_MAX_AGE, content_length=None, content_type=None):
    if not (static_page.layout_id and has_renderer(request, fullpath)):
        return FileLikeResponse(io, request=request, cache_max_age=cache_max_age, content_type=content_type, content_length=content_length, 
                                app_iter=None, _BLOCK_SIZE=4096)
    resolver = get_frontpage_discriptor_resolver(request)
    discriptor = resolver.resolve(request, static_page.layout, verbose=True)
    if not discriptor.exists():
        return FileLikeResponse(io, request=request, cache_max_age=cache_max_age, content_type=content_type, content_length=content_length, 
                                app_iter=None, _BLOCK_SIZE=4096)
    try:
        params = {body_var_name: io.read().decode("utf-8"), 
                  "static_page": static_page} #ok?
    except Exception, e:
        logger.exception(str(e))
        params = {body_var_name: ""}
    return render_to_response(discriptor.absspec(), params, request)
