from . import base
from . import front
from . import asset
from . import event
from . import page
from . import widget
from . import tag
from . import link
__all__ = ["base", "front", "asset", "event", "page", "widget", "tag",  "link"]

## pagination
from webhelpers.paginate import Page

def url_generate_default(request, **kwargs):
    curpath = request.current_route_path(**kwargs)
    def _url(page=None, **kwargs):
        return "%s?page=%s" % (curpath, page)
    return _url

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
