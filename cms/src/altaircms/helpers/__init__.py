from . import base
from . import asset
from . import event
from . import page
from . import widget
from . import tag
from . import link
from . import mobilelink
__all__ = ["base", "asset", "event", "page", "widget", "tag", "link", "mobilelink"]

## pagination
from webhelpers.paginate import Page
import urlparse
import cgi 
import itertools

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
        return url_create_with_parse_result(parse_result, page=page)
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

paginate = PagerAdapter
