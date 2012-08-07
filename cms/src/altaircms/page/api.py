# -*- encoding:utf-8 -*-

import os
import sqlalchemy as sa
from altaircms.solr import api as solr
from ..interfaces import IDirectoryResource
from pyramid.exceptions import ConfigurationError
from pyramid.path import AssetResolver
from .models import StaticPage
from markupsafe import Markup
### static page
def get_static_page_utility(request):
    return request.registry.getUtility(IDirectoryResource, "static_page")

def set_static_page_utility(config, basedir):
    utility = StaticPageDirectory(basedir)
    utility.validate()
    return config.registry.registerUtility(utility, IDirectoryResource, "static_page")

class StaticPageDirectory(object):
    def __init__(self, basedir, tmpdir="/tmp"):
        self.assetresolver = AssetResolver()
        self.assetspec = basedir
        self.basedir = self.assetresolver.resolve(basedir).abspath()
        self.tmpdir = self.assetresolver.resolve(tmpdir).abspath()

    def validate(self):
        if os.path.exists(self.basedir):
            if not os.path.isdir(self.basedir):
                raise ConfigurationError("%s is not directory" % self.basedir)
        else:
            os.makedirs(self.basedir)
        return True

    def get_base_directory(self):
        return self.basedir

    def get_managemented_files(self, request):
        return request.allowable(StaticPage).order_by(sa.desc("updated_at"))

    # def get_static_page_children(self, static_page):
    #     path = os.path.join(self.basedir, static_page.name)
    #     return os.listdir(path)

    ## helpers
    def link_from_file(self, request, static_page, path):
        asset_path = os.path.join(self.assetspec, static_page.name, path)
        return request.static_url(asset_path)
    
    def link_tree_from_static_page(self, request, static_page):
        root = os.path.join(self.basedir, static_page.name)
        return Markup(u"\n".join(self._link_tree_from_static_page(request, root, [])))
    
    def _link_tree_from_static_page(self, request,  path, r):
        if os.path.isdir(path):
            r.append(u"<li>%s</li>" % os.path.basename(path))
            r.append(u"<ul>")
            for subpath in os.listdir(path):
                self._link_tree_from_static_page(request, os.path.join(path, subpath), r)
            r.append(u"</ul>")
        else:
            r.append(u"<li>")
            href = request.static_url(path.replace(self.basedir, self.assetspec))
            r.append(u'<a href="%s">%s</a>' % (href, os.path.basename(path)))
            r.append(u"</li>")
        return r

### solr
def doc_from_tags(doc, tags):
    vs = [tag.label for tag in tags]
    doc.update(page_tag=vs)
    return doc 

def doc_from_performances(doc, performances):
    vs = [p.venue for p in performances]
    doc.update(performance_venue=vs)
    return doc

def _split_text(text):
    if text is None:
        return []
    tags = [e.strip() for e in text.split(",")] ##
    return [k for k in tags if k]

def doc_from_event(doc, event): ## fixme
    doc.update(event_title=event.title, 
               event_subtitle=event.subtitle, 
               event_performer=_split_text(event.performers), 
               event_description=event.description)
    return doc 

def _doc_from_page(doc, page):
    doc.update(page_description=page.description, 
               page_title=page.title, 
               page_id=page.id)
    if page.pageset:
        doc.update(id=page.pageset.id, 
                   pageset_id=page.pageset.id)
    return doc
    
def doc_from_page(page):
    """ id == page.pageset.id 
    """
    doc = solr.SolrSearchDoc()
    event = page.event or (page.pageset.event if page.pageset else None) #for safe
    if event:
        doc = doc_from_event(doc, event)
        doc = doc_from_performances(doc, event.performances)

    tags = page.public_tags
    if tags:
        doc = doc_from_tags(doc, tags)
        
    _doc_from_page(doc, page)
    return doc


def ftsearch_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = doc_from_page(page)
    ftsearch.register(doc, commit=True)

def ftsearch_delete_register_from_page(request, page, ftsearch=None):
    ftsearch = ftsearch or solr.get_fulltext_search(request)
    doc = solr.create_doc_from_dict({"page_id": page.id})
    ftsearch.delete(doc, commit=True)
    

