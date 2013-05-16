from altaircms.helpers import url_create_with
from pyramid.path import AssetResolver
import sqlalchemy as sa
from markupsafe import Markup
import functools
import os
from pyramid.exceptions import ConfigurationError
from pyramid.interfaces import IRendererFactory
from pyramid.response import FileResponse
from pyramid.renderers import render_to_response

import logging
logger = logging.getLogger(__name__)

from ...interfaces import IDirectoryResource
from .. import StaticPageNotFound
from ..models import StaticPage
from altairsite.front.api import get_frontpage_discriptor_resolver

def has_renderer(request, path):
    ext = os.path.splitext(path)[1]
    return bool(request.registry.queryUtility(IRendererFactory, name=ext))

CACHE_MAX_AGE=60
def as_wrapped_resource_response(request, static_page, fullpath, body_var_name="inner_body"):
    if not (static_page.layout_id and has_renderer(request, fullpath)):
        return FileResponse(fullpath, request=request, cache_max_age=CACHE_MAX_AGE)
    resolver = get_frontpage_discriptor_resolver(request)
    discriptor = resolver.resolve(request, static_page.layout, verbose=True)
    if not discriptor.exists():
        return FileResponse(fullpath, request=request, cache_max_age=CACHE_MAX_AGE)
    try:
        params = {body_var_name: open(fullpath).read().decode("utf-8"), 
                  "static_page": static_page} #ok?
    except Exception, e:
        logger.exception(str(e))
        params = {body_var_name: ""}
    return render_to_response(discriptor.absspec(), params, request)


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

class StaticPageDirectory(object):
    def __init__(self, basedir, tmpdir="/tmp", request=None):
        self.request = request
        self.assetresolver = AssetResolver()
        self.assetspec = basedir
        self.basedir = self.assetresolver.resolve(basedir).abspath()
        self.tmpdir = self.assetresolver.resolve(tmpdir).abspath()


    def get_base_directory(self):
        return os.path.join(self.basedir, self.request.organization.short_name)

    def rename(self, src, dst):
        logger.info("rename static pages: %s -> %s" % (src, dst))
        return os.rename(os.path.join(self.get_base_directory(), src), 
                         os.path.join(self.get_base_directory(), dst))

    def get_managemented_files(self, request):
        return request.allowable(StaticPage).order_by(sa.desc(StaticPage.updated_at))

    def validate(self):
        return directory_validate(self.basedir, self.tmpdir)

    # def get_static_page_children(self, static_page):
    #     path = os.path.join(self.basedir, static_page.name)
    #     return os.listdir(path)

    ## helpers
    def link_from_file(self, request, static_page, path):
        asset_path = os.path.join(self.assetspec, static_page.name, path)
        return request.static_url(asset_path)
    
    def link_tree_from_static_page(self, request, static_page):
        basedir = self.get_base_directory()
        root = os.path.join(basedir, static_page.name)
        return Markup(u"\n".join(self._link_tree_from_static_page(request, root, [], basedir)))
    
    def _link_tree_from_static_page(self, request,  path, r, basedir):
        if os.path.isdir(path):
            r.append(u"<li>%s</li>" % os.path.basename(path))
            r.append(u"<ul>")
            for subpath in os.listdir(path):
                self._link_tree_from_static_page(request, os.path.join(path, subpath), r, basedir)
            r.append(u"</ul>")
        else:
            r.append(u"<li>")
            preview_url = request.route_path("static_page_display",  path=path.replace(basedir, "")).replace("%2F", "/")
            # href = request.static_url(path.replace(self.basedir, self.assetspec))
            # r.append(u'<a href="%s">%s</a>(<a href="%s">original</a>)' % (preview_url, os.path.basename(path), href))
            if request.GET:
                r.append(u'<a href="%s">%s</a>' % (url_create_with(preview_url, **request.GET), os.path.basename(path)))
            else:
                r.append(u'<a href="%s">%s</a>' % (preview_url, os.path.basename(path)))
            r.append(u"</li>")
        return r

def as_static_page_response(request, static_page, url, force_original=False):
    static_page_utility = get_static_page_utility(request)
    if url.startswith("/"):
        url_parts = url[1:]
    else:
        url_parts = url

    fullpath = os.path.join(static_page_utility.get_base_directory(), url_parts)
    if os.path.exists(fullpath) and os.path.isfile(fullpath):
        if force_original:
            return FileResponse(fullpath, request=request, cache_max_age=CACHE_MAX_AGE)
        else:
            return as_wrapped_resource_response(request, static_page, fullpath)
    else:
        msg = "%s is not found" % fullpath
        logger.info(msg)
        raise StaticPageNotFound(msg)

def get_static_page_utility(request):
    return request.registry.getUtility(IDirectoryResource, "static_page")(request=request)

def set_static_page_utility(config, basedir, tmpdir):
    utility = functools.partial(StaticPageDirectory, basedir, tmpdir=tmpdir)
    resolver = AssetResolver()
    directory_validate(resolver.resolve(basedir).abspath(), resolver.resolve(tmpdir).abspath())
    return config.registry.registerUtility(utility, IDirectoryResource, "static_page")
