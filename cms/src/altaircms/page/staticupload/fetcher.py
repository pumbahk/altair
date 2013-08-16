# -*- coding:utf-8 -*-
import re
import os
import urllib
from datetime import datetime
from zope.interface import implementer
from pyramid.response import FileResponse
from pyramid.response import Response
from pyramid.interfaces import IRendererFactory
from pyramid.renderers import render_to_response
from pyramid.decorator import reify

import logging
logger = logging.getLogger(__name__)

from .interfaces import IStaticPageDataFetcher
from .interfaces import IStaticPageCache
from .. import StaticPageNotFound
from altairsite.front.api import get_frontpage_discriptor_resolver
from altaircms.response import FileLikeResponse
from collections import namedtuple

CACHE_MAX_AGE=60

def has_renderer(request, path):
    ext = os.path.splitext(path)[1]
    return bool(request.registry.queryUtility(IRendererFactory, name=ext))


FetchData = namedtuple("FetchData", "path, size, code, data, type, content_type, group_id")
#type = io, string, filepath
class _Unknown(object):
    pass
unknown = _Unknown()

@implementer(IStaticPageDataFetcher)
class FetcherFromFileSystem(object):
    def __init__(self, request, static_page, utility):
        self.request = request
        self.static_page = static_page
        self.utility = utility

    def fetch(self, url, path):
        if path is None: #xxx:
            if self.static_page.pageset.url == "":
                path = os.path.join(self.utility.get_rootname(self.static_page), url)            
            else:
                if url.startswith("/"):
                    url_parts = url[1:]
                else:
                    url_parts = url
                    url_parts = "/".join(url_parts.split("/")[1:]) #foo/bar -> bar
                path = os.path.join(self.utility.get_rootname(self.static_page), url_parts)
        return FetchData(code=unknown, size=unknown, path=path, data=path, type="filepath", content_type=unknown, group_id=unicode(self.static_page.id))

@implementer(IStaticPageDataFetcher)
class FetcherFromNetwork(object):
    def __init__(self, request, static_page, utility):
        self.request = request
        self.static_page = static_page
        self.utility = utility

    # def convert_extname(self, filepath):
    #     ## hmm. /foo -> /foo.html,  /foo/ -> /foo/
    #     base, ext = os.path.splitext(filepath)
    #     if ext == "" and not base.endswith("/"):
    #         return filepath + ".html"
    #     else:
    #         return filepath
    def _split_page_prefix(self,file_path):
        try:
            prefix, file_path = file_path.split("/", 1)
        except ValueError:
            logger.info("{file_path} is toplevel path".format(file_path=file_path))
        return file_path

    def check_skip_fetch(self, url, path):
        if not path:
            file_path = url[1:] if url.startswith("/") else url
            file_path = self._split_page_prefix(file_path)
            if not file_path in self.static_page.file_structure:
                logger.info("{0} is not found in {1}".format(file_path, self.static_page.file_structure_text))
                raise StaticPageNotFound("{0} is not found".format(file_path))
        
    def fetch(self, url, path):
        if path:     
            io = urllib.urlopen(self.utility.get_url(path))
            url_parts = path
        else:
            file_path = url[1:] if url.startswith("/") else url
            file_path = self._split_page_prefix(file_path)
            # file_path = self.convert_extname(file_path)
            url_parts = "/{0}/{1}/{2}/{3}".format(self.request.organization.short_name, self.static_page.prefix, self.static_page.id, file_path)
            logger.debug("url:{url}".format(url=self.utility._get_url(url_parts)))
            io = urllib.urlopen(self.utility._get_url(url_parts))
        try:
            size = int(io.info().get("Content-Length", "0"))
        except ValueError:
            size = 0
        if io.getcode() != 200:
            logger.info("static page response not success: url={0}, code={1}".format(io.geturl(), io.getcode()))
            return FetchData(code=io.getcode(), size=size, data=io, type="socket", content_type=io.info().typeheader, path=url_parts, group_id=unicode(self.static_page.id))
        return FetchData(code=200, size=size, data=io, type="socket", content_type=io.info().typeheader, path=url_parts, group_id=unicode(self.static_page.id))

CHARSET_RX = re.compile(r"charset=([^ ]+)")

@implementer(IStaticPageDataFetcher)
class CachedFetcher(object):
    def __init__(self, fetcher, cache_impl):
        self.fetcher = fetcher
        self.cache_impl = cache_impl

    @property
    def request(self):
        return self.fetcher.request
    @property
    def utility(self):
        return self.fetcher.utility
    @property
    def static_page(self):
        return self.fetcher.static_page

    def make_key(self, url, path):
        static_page = self.static_page
        url = self.utility.get_url(path) if path else url
        return '{id}@{version}@{url}'.format(id=static_page.id, version=static_page.uploaded_at, url=url)

    def fetch(self, url, path):
        k = self.make_key(url, path)
        if hasattr(self.fetcher, "check_skip_fetch"):
            self.fetcher.check_skip_fetch(url, path)
        try:
            return self.cache_impl[k]
        except KeyError:
            def fetch_function(cache, k):
                data = self.fetcher.fetch(url, path)
                content_type = data.content_type

                ### takeout from webob.response
                if content_type and (content_type == 'text/html'
                                     or content_type.startswith(('text/', 'application/xml', 'application/json'))
                                     or (content_type.startswith('application/')
                                         and (content_type.endswith('+xml') or content_type.endswith('+json')))):

                    if 'charset=' in content_type:
                        encoding = CHARSET_RX.match(content_type).group(1).strip()
                    else:
                        encoding = 'utf-8' #xxx:
                    content = data.data.read().decode(encoding)
                else:
                    content = data.data.read()
                data = FetchData(code=data.code, size=data.size, data=content,
                                 type="string", content_type=data.content_type, path=data.path, group_id=data.group_id)
                return data
            return self.cache_impl.on_fetching_self(k, fetch_function)

## cache
from beaker.cache import Cache
from pyramid.httpexceptions import HTTPNotFound

@implementer(IStaticPageCache)
class StaticPageCache(object):
    def __init__(self, kwargs):
        self.file_data = Cache._get_cache("file_data", kwargs) #xxx:
        self.fetching = Cache._get_cache("fetching", kwargs) #xxx:
        self.file_group = Cache._get_cache("file_group", kwargs) #xxx:

    def on_fetching_another(self, k):
        logger.info("fetching: fetching another process. '{k}'".format(k=k))
        raise HTTPNotFound("fetching another") #hmm.

    def on_fetching_self(self, k, fetch_function):
        now = datetime.now()
        self.fetching[k] = now
        logger.debug("StaticPageCache: fetch -- {k}, fetching={now}".format(k=k, now=now))
        try:
            v = fetch_function(self, k)
            logger.debug("StaticPageCache: setitem and remove sentinel -- {k}, fetching=removed".format(k=k))
            self.fetching.remove_value(k)
            if not v.group_id in self.file_group:
                self.file_group[v.group_id] = {k}
            else:
                cached = self.file_group[v.group_id]
                cached.add(k)
                self.file_group[v.group_id] = cached
            self.file_data[k] = v
            # logger.debug("result: group={group} data={data}".format(group=self.file_group[v.group_id], data=v)) #annoying
            return v
        except Exception as e:
            logger.exception(str(e))
            logger.warn("fetching: exception found. on fetching data. release for '{k}'".format(k=k))
            self.fetching.remove_value(k)

    def remove_group(self, k):
        try:
            group = self.file_group[k]
            for f in group["files"]:
                self.file_data.remove_value(f)
        except KeyError:
            logger.info("group: {k} is not found".format(k=k))

    def __getitem__(self, k):
        try:
            logger.debug("StaticPageCache: getitem -- {k}".format(k=k))
            return self.file_data[k]
        except KeyError:
            logger.debug("StaticPageCache: notfound -- {k}".format(k=k))
            if k in self.fetching:
                logger.debug("StaticPageCache: fetching is exists -- {k}".format(k=k))
                return self.on_fetching_another(k)
            raise

class ResponseMaker(object):
    NotFound = StaticPageNotFound
    def __init__(self, request, static_page, 
                 force_original=False, 
                 cache_max_age=None, body_var_name="inner_body"):
        self.request = request
        self.static_page = static_page
        self.force_original = force_original
        self.cache_max_age = cache_max_age
        self.body_var_name = body_var_name

    @reify
    def descriptor(self):
        resolver = get_frontpage_discriptor_resolver(self.request)
        return resolver.resolve(self.request, self.static_page.layout, verbose=True)
        
    def is_ordinary_file(self, fullpath):
        return not (self.static_page.layout_id and has_renderer(self.request, fullpath))

    def ordinary_response(self, data):
        if data.type == "string":
            return Response(data.data, content_type=data.content_type, content_length=data.size) #xxx
        elif data.type == "filepath":
            return FileResponse(data.path, request=self.request, cache_max_age=self.cache_max_age)
        elif data.type == "socket":
            if data.code != 200:
                raise self.NotFound("url={url}, data={data}".format(url=data.data.geturl(), data=data))
            return FileLikeResponse(data.data, request=self.request, 
                                    cache_max_age=self.cache_max_age, content_type=data.content_type, content_length=data.size, 
                                    app_iter=None, _BLOCK_SIZE=4096)
        else:
            logger.error("ordinary response: type={type} is not found".format(type=data.type))
            raise self.NotFound() #xxx:

    def make_response(self, data):
        if self.force_original:
            return self.ordinary_response(data)
        if self.is_ordinary_file(data.path):
            return self.ordinary_response(data)
        if not self.descriptor.exists():
            return self.ordinary_response(data)

        if data.type == "string":
            return self.make_response_from_string(data)
        elif data.type == "filepath":
            return self.make_response_from_filepath(data)
        elif data.type == "socket":
            return self.make_response_from_socket(data)
        else:
            logger.error("make response: type={type} is not found".format(type=data.type))
            raise self.NotFound() #xxx:

    def make_response_from_string(self, data):
        params = {self.body_var_name: data.data, 
                  "static_page": self.static_page} #ok?
        return self.render(self.descriptor.absspec(), params)

    def make_response_from_filepath(self, data):
        assert data.data == data.path
        fullpath = data.data
        try:
            params = {self.body_var_name: open(fullpath).read().decode("utf-8"), 
                      "static_page": self.static_page} #ok?
        except (IOError, OSError):
            msg = "filesystem %s is not found" % fullpath
            logger.info(msg)
            raise self.NotFound(msg)
        except Exception as e:
            logger.exception(str(e))
            params = {self.body_var_name: ""}
        return self.render(self.descriptor.absspec(), params)

    def make_response_from_socket(self, data):
        try:
            params = {self.body_var_name: data.data.read().decode("utf-8"), 
                      "static_page": self.static_page} #ok?
        except (IOError, OSError):
            msg = "network: %s is not found" % data.path
            logger.info(msg)
            raise StaticPageNotFound(msg)
        except Exception as e:
            logger.exception(str(e))
            params = {self.body_var_name: "", "static_page": self.static_page} #ok?
        return self.render(self.descriptor.absspec(), params)

    def render(self, spec, params):
        try:
            return render_to_response(spec, params, self.request)
        except Exception as e:
            logger.exception(e)
            raise StaticPageNotFound("exception is occured")
