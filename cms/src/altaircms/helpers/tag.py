# -*- coding:utf-8 -*-

import urllib

def show_public_status(tag):
    return u"公開タグ" if tag.publicp else u"非公開タグ"

def to_search(request, classifier=None):
    if classifier is None:
        return request.route_path("tag", classifier="top")
    else:
        params = dict(request.GET)
        params["classifier"] = classifier
        return u"%s?%s" % (request.route_path("tag", classifier=classifier), 
                           urllib.urlencode(params))

def to_search_query(request, classifier, tag):
    params = dict(classifier=classifier, query=tag.label)
    return u"%s?%s" % (request.route_path("tag", classifier=classifier), 
                       urllib.urlencode(params))

    

