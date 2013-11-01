# -*- coding:utf-8 -*-

import urllib

## todo: 以下のクラスを利用している箇所のimport文変更
from .modelmanage import (
    ApplicableTicketsProducer, 
    IssuedAtBubblingSetter, 
    PrintedAtBubblingSetter, 
    IssuedPrintedAtSetter, 
)

def tree_dict_from_flatten(d, sep):
    result = {}
    for master_key in d:
        ks = sep(master_key)
        if len(ks) <= 1:
            result[master_key] = d[master_key]
        else:
            target = result
            for k in ks[:-1]:
                if not k in target:
                    target[k] = {}
                target = target[k]
            target[ks[-1]] = d[master_key]
    return result

def merge_dict_recursive(d1, d2): #muttable!. not support list. only atom and dict.
    for k, v in d2.iteritems():
        if not hasattr(v, "iteritems") or not k in d1:
            d1[k] = v
        else:
            sub = d1[k]
            if not hasattr(sub, "iteritems"):
                d1[k] = v
            else:
                merge_dict_recursive(sub, v)
    return d1

class PageURL_WebOb_Ex(object):
    def __init__(self, request, encode_type="utf-8", qualified=False):
        self.request = request
        self.encode_type = encode_type
        self.qualified = qualified

    def __call__(self, page, partial=False):
        if self.qualified:
            path = self.request.application_url
        else:
            path = self.request.path
        return make_page_url(path, self.request.GET, page, self.encode_type, partial)

def make_page_url(path, params, page, encode_type, partial=False):
    params = params.copy()
    params["page"] = page
    if partial:
        params["partial"] = "1"

    qs = urllib.urlencode(dict([k, v.encode(encode_type) if isinstance(v, unicode) else v] for k, v in params.items()))
    return "%s?%s" % (path, qs)
