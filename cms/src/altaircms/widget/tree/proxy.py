import json
from collections import defaultdict
from altaircms.interfaces import IBlockTree
from altaircms.interfaces import ICacher
from zope.interface import implements
from altaircms.widget.fetcher import WidgetFetcher


"""
get structure from page and get widget tree from structure.
"""

class WidgetTreeGenerateException(Exception):
    pass

class WidgetTreeProxy(object):
    """ a facade for one page object.
    """
    implements(IBlockTree)
    def __init__(self, page, session=None):
        self.page = page
        self.cacher = WidgetCacher(WidgetFetcher(session=session))
        self.tree = None
    
    def _get_tree(self):
        self.tree = self.cacher.to_widget_tree(self.page)
        return self.tree

    @property
    def blocks(self):
        if self.tree:
            return self.tree.blocks
        return self._get_tree().blocks


class WidgetTree(object):
    implements(IBlockTree)

    def __init__(self):
        self.blocks = defaultdict(list)

    def add(self, block_name, obj):
        self.blocks[block_name].append(obj)

    def adds(self, block_name, objs):
        self.blocks[block_name].extend(objs)

def _structure_as_dict(page):
    if page.structure is None:
        return {}
    try:
        return json.loads(page.structure)
    except ValueError, e:
        raise WidgetTreeGenerateException(str(e))
    
class WidgetCacher(object):
    """
    u'{
       "content": [{"pk": 1, "name": "freetext_widget"}],
       "footer": [{"pk": 2, "name": "image_widget"}]
       }'
    """
    implements(ICacher)
    def __init__(self, fetcher):
        self.kinds = defaultdict(list)
        self.result = defaultdict(dict)
        self.scanned = {}
        self.fetched = False
        self.fetcher = fetcher

    def is_scanned(self, page):
        return page is None or self.scanned.get(page)

    def scan(self, page):
        if self.is_scanned(page):
            return
        for blocks in _structure_as_dict(page).values():
            for block in blocks:
                self.kinds[block["name"]].append(block["pk"])
        self.scanned[page] = True
        self.fetched = False

    def fetch(self):
        if self.fetched:
            return
        for name, pks in self.kinds.items():
            objs = self.fetcher.fetch(name, pks)
            for obj in objs:
                self.result[name][obj.id] = obj
        self.fetched = True

    def to_widget_tree(self, page):
        if not self.is_scanned(page):
            self.scan(page)
        if not self.fetched:
            self.fetch()
        tree = WidgetTree()
        for block_name, blocks in _structure_as_dict(page).items():
            objs = []
            for o in blocks:
                widgets = self.result[o["name"]]
                if widgets.get(o["pk"]):
                    objs.append(widgets[o["pk"]])
                ## a widget's content is empty, then skipped
            tree.adds(block_name, objs)
        return tree
