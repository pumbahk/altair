import urllib

def to_search(request, classifier):
    if classifier is None:
        return request.route_path("tag")
    else:
        params = dict(request.GET)
        params["classifier"] = classifier
        return u"%s?%s" % (request.route_path("tag", classifier=classifier), 
                           urllib.urlencode(params))


