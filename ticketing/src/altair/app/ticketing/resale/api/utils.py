# encoding: utf-8

from urllib import urlencode
from urlparse import urlsplit, urlunsplit, parse_qs

def ensure_positive_int(int_str, strict=False, cutoff=None):
    ret = int(int_str)
    if ret < 0 or (ret == 0 and strict):
        raise ValueError()
    if cutoff:
        ret = min(ret, cutoff)
    return ret

def replace_url_query_param(url, param, val):
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    query_dict = parse_qs(query)
    query_dict[param] = val
    query = urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlunsplit((scheme, netloc, path, query, fragment))

def remove_url_query_param(url, param):
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    query_dict = parse_qs(query)
    query_dict.pop(param, None)
    query = urlencode(sorted(list(query_dict.items())), doseq=True)
    return urlunsplit((scheme, netloc, path, query, fragment))