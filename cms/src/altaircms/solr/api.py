# -*- encoding:utf-8 -*-

import solr
import logging
logger = logging.getLogger(__name__)
from zope.interface import implementer
from pyramid.decorator import reify
from .interfaces import IFulltextSearch
import random

def get_fulltext_search(request):
    search_cls = request.registry.getUtility(IFulltextSearch)
    return search_cls.create_from_request(request)

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
            return (u"(%s:%s)" % (k, v) for k, v in self.kwargs.iteritems())
        else:
            return (u"(%s)" % e.query_string for e in self.kwargs)

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

def _create_dict_from_word(word):
    """ 検索用の辞書作る
    solrに格納される各フィールドはcopyfieldとしてsearchtextが設定されている。
    (see: buildout.cfg 'solr' section)
    """
    return dict(searchtext=word)
    
def create_query_from_freeword(words, query_cond=None):
    assert query_cond in ("intersection", "union")
    
    if query_cond == "intersection":
        cop = u" AND "
    elif query_cond == "union":
        cop = u" OR "

    q = SolrSearchQuery(_create_dict_from_word(words[0]))
    for word in words[1:]:
        q = q.compose(SolrSearchQuery(_create_dict_from_word(word)), cop)
    return q

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
        logger.debug(u"fulltext search query: %s" % query)
        return self.solr.select(query.query_string, **kwargs).results

    def register(self, doc, commit=False):
        logger.debug(u"fulltext search register: %s" % doc)
        self.solr.add(doc.query_doc, commit=commit)

        ## 5回に1回位はoptimizeした方が良いらしい。
        # if 0.2 >= random.random():
        #     self.solr.optimize()

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
