import urlparse

def _parse_result_update(parse_result, **kwargs):
    scheme, netloc, url, params, query, fragment = parse_result
    D = {}
    D["scheme"] = scheme
    D["netloc"] = netloc
    D["url"] = url
    D["params"] = params
    D["query"] = query
    D["fragment"] = fragment
    D.update(kwargs)
    return urlparse.ParseResult(**D)

# data = urlparse.urlparse("http://foo.bar.bab")
# _parse_result_update(data)
# def masked_url(url, sym="*"):
    
