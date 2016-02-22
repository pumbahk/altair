# -*- coding:utf-8 -*-
import urllib
from . import base
from . import asset
from . import event
from . import page
from . import widget
from . import tag
from . import link
from . import mobilelink
from . import access
from xml.etree import ElementTree
__all__ = ["base", "asset", "event", "page", "widget", "tag", "link", "mobilelink", "access"]

## pagination
from webhelpers.paginate import Page
import urlparse
import cgi 
import itertools
from markupsafe import Markup
from altair.viewhelpers import truncate, truncate_eaw, first_and_last

def url_create_with(url, **kwargs):
    """
    # identity
    >>> url_create_with('/foo?bar=boo&x=y')
    '/foo?bar=boo&x=y'

    # paramater replace
    >>> url_create_with('/foo?bar=boo&x=y', x='z')
    '/foo?bar=boo&x=z'

    # paramater replace + add paramater
    >>> url_create_with('/foo?bar=boo&x=y', x='z', hey='yah')
    '/foo?bar=boo&x=z&hey=yah'
    """
    parse_result = urlparse.urlparse(url)
    return url_create_with_parse_result(parse_result, **kwargs)

def url_create_with_parse_result(parse_result, **kwargs):
    queries = cgi.parse_qsl(parse_result.query, keep_blank_values=True)
    queries = [(k, kwargs.pop(k) if k in kwargs else v) for k, v in queries]
    queries = itertools.chain(queries, kwargs.iteritems())
    query = "&".join("%s=%s" % (k, v) for k, v in queries)
    return unparse_with_replace_query(parse_result, query)

def unparse_with_replace_query(parse_result, query):
    ## from urlparse.urlunparse
    scheme, netloc, url, params, _, fragment = parse_result
    if params:
        url = "%s;%s" % (url, params)
    return urlparse.urlunsplit((scheme, netloc, url, query, fragment))

def url_generate_default(request, **kwargs):
    """pagination default url generator"""
    curpath = request.url
    parse_result = urlparse.urlparse(curpath)

    def replacement(page, **kwargs):
        return safe_url_quote(url_create_with_parse_result(parse_result, page=page))
    return replacement

class PagerAdapter(object):
    DEFAULT_OPT = {"items_per_page": 10, 
                   "page": 1}
    DEFAULT_PAGER_OPT = {
        "format": "$link_first $link_previous ~3~ $link_next $link_last"
        }

    def __init__(self, request, collection, **kwargs):
        self.opts = self.DEFAULT_OPT.copy()
        self.opts.update(kwargs)
        if "page" in request.GET:
            if request.GET["page"].isdigit():
                self.opts["page"] = int(request.GET["page"])
        if not "url" in self.opts:
            self.opts["url"] = url_generate_default(request)

        self.pagination = Page(collection, **self.opts)
        self.collection = collection

    def __getattr__(self, k, v=None):
        return getattr(self.pagination, k, v)

    def paginated(self):
        items_per_page = self.opts["items_per_page"]
        n = (self.opts["page"] - 1) * items_per_page

        if hasattr(self.collection, "offset"):
           ## query object of sqlalchemy
            return self.collection.offset(n).limit(items_per_page)
        else:
           ## list like object
            return self.collection[n:n+items_per_page]

    def pager(self, **kwargs):
        opts = self.DEFAULT_PAGER_OPT.copy()
        opts.update(kwargs)
        return self.pagination.pager(**opts)

    def pager_value(self, key):
        return self.pagination.pager(key)

    def link_str(self, link):
        doc = self.pagination.pager(link)
        if doc:
            root = ElementTree.fromstring(doc)
            return root.attrib["href"]
        return None

paginate = PagerAdapter

jterm = term = base.date_time_helper.term
term_datetime = base.date_time_helper.term_datetime

def _merge_dict(base, other=None, dels=None):
    r = {}
    r.update(base)
    if other:
        r.update(other)
    if dels:
        for k in dels:
            if k in r:
                del r[k]
    return r
    
def route_path_override(request, path, _query=None, _dels=None, **kwargs):
    qdict = _merge_dict(request.GET, other=_query, dels=_dels)
    return request.route_path(path, _query=qdict, **kwargs)

def current_route_path_override(request, _query=None, _dels=None, **kwargs):
    qdict = _merge_dict(request.GET, other=_query, dels=_dels)
    return request.current_route_path(_query=qdict, **kwargs)

def safe_url_quote(url):
    try:
        return urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]").decode("utf-8") if url else ""
    except KeyError:
        try:
            return urllib.quote(url.encode("utf-8"), safe="%/:=&?~#+!$,;'@()*[]").decode("utf-8") if url else ""
        except:
            return ""

def chunk(i, count, cons=list):
    i = iter(i)
    while True:
        l = cons(itertools.islice(i, count))
        if not l:
            break
        yield l
