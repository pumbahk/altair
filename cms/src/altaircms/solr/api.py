# -*- encoding:utf-8 -*-

import solr
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from pyramid.decorator import reify
from altaircms.solr.interfaces import IFulltextSearch
import random


def pageset_id_list_from_word(request, word):
    fulltext_search = get_fulltext_search(request)
    query = _create_query_from_word(word)
    result = fulltext_search.search(query, fields=["pageset_id"])
    return [f["pageset_id"] for f in result]

def get_fulltext_search(request):
    search_cls = request.registry.getUtility(IFulltextSearch)
    return search_cls.create_from_request(request)

def _create_query_from_word(word):
    """ 検索用の辞書作る
    solrに格納される各フィールドはcopyfieldとしてsearchtextが設定されている。
    (see: buildout.cfg 'solr' section)
    """
    return SolrSearchQuery(dict(searchtext=word))
    
def create_query_from_freewords(words, query_cond=None):
    assert query_cond in ("intersection", "union")
    
    if query_cond == "intersection":
        cop = u" AND "
    elif query_cond == "union":
        cop = u" OR "

    q = _create_query_from_word(words[0])
    for word in words[1:]:
        q = q.compose(_create_query_from_word(word), cop)
    return q


class NullSearchQuery(object):
    def AND(self, other):
        return SolrSearchQuery(other, cop=" AND ")

    def OR(self, other):
        return SolrSearchQuery(other, cop=" OR ")

class SolrSearchQuery(object):
    def __init__(self, kwargs, cop=None):
        self.kwargs = kwargs
        self.cop = cop or u" OR "

    def __repr__(self):
        return str(self.kwargs)

    def query_iter(self):
        if isinstance(self.kwargs, dict):
            return (u'(%s:%s)' % (k, v) for k, v in self.kwargs.iteritems())
        else:
            return (u'(%s)' % e.query_string for e in self.kwargs)

    def NOT(self):
        return NSolrSearchQuery([self])
    
    def compose(self, other, cop):
        return SolrSearchQuery([self, other], cop=cop)

    def AND(self, other):
        return SolrSearchQuery([self, other], cop=" AND ")

    def OR(self, other):
        return SolrSearchQuery([self, other], cop=" OR ")

    @property
    def query_string(self):
        return self.cop.join(e for e in self.query_iter())

class NSolrSearchQuery(SolrSearchQuery):
    @property
    def query_string(self):
        return u"NOT %s" % super(NSolrSearchQuery, self).query_string

class SolrSearchDoc(object):
    def __init__(self, doc=None):
        self.doc = doc or {}
    
    def __repr__(self):
        return str(self.doc)

    def update(self, _D=None, **kwargs):
        if _D:
            kwargs.update(_D)
        self.doc.update(kwargs)

    @reify
    def query_doc(self):
        return self.doc

## query
def create_query_from_dict(D__=None, **kwargs):
    return SolrSearchQuery(D__ or kwargs)
## doc
def create_doc_from_dict(D):
    return SolrSearchDoc(D)              

@implementer(IFulltextSearch)
class SolrSearch(object):
    """ fulltext search via solr
    """
    SETTINGS_KEY_NAME = "altaircms.solr.server.url"

    @classmethod
    def create_from_request(cls, request):
        settings = request.registry.settings
        return cls(settings[cls.SETTINGS_KEY_NAME])

    def __init__(self, server_url):
        self.server_url = server_url

    @reify
    def solr(self):
        return solr.Solr(self.server_url)

    def commit(self):
        return self.solr.commit()

    def search(self, query, **kwargs):
        logger.info(u"fulltext search query: %s" % query.query_string)
        result = self.solr.select(query.query_string, **kwargs)
        logger.info("fulltext search result %s" % result.results)
        return result.results

    def register(self, doc, commit=False):
        logger.debug(u"fulltext search register: %s" % doc)
        if not "id" in doc.query_doc:
            logger.warn("id is not found %s" % doc.query_doc)
            return
        self.solr.add(doc.query_doc, commit=commit)

        # 5回に1回位はoptimizeした方が良いらしい。
        if 0.2 >= random.random():
            self.solr.optimize()

    def delete(self, doc, commit=False):
        logger.debug(u"fulltext search delete: %s" % doc)
        self.solr.delete(doc.query_doc)
        if commit:
            self.solr.commit()

@implementer(IFulltextSearch)
class DummySearch(object):
    @classmethod
    def create_from_request(cls, request):
        return cls()

    def search(self, query, **kwargs):
        logger.info(u"fulltext search query: %s" % query)
        return []

    def register(self, doc, *args, **kwargs):
        logger.info(u"fulltext search register: %s" % doc)

    def delete(self, doc, *args, **kwargs):
        logger.info(u"fulltext search delete: %s" % doc)

if __name__ == "__main__":
    query = create_query_from_freewords([u"abc", "def"], query_cond="intersection")
    print query.query_string

