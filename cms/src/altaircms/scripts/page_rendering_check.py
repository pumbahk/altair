import argparse
import urllib
import traceback
from pyramid.scripting import _make_request
from pyramid.paster import bootstrap
from pyramid.scripts.common import logging_file_config
from altaircms.auth.interfaces import IAllowableQuery
import sys

def check_rendering(router, request):
    try:
        sys.stderr.write(".")
        sys.stderr.flush()
        response = router.handle_request(request)
        if response.status_int != 200:
            print request._pageset.id, 
            print response.status
    except:
        print traceback.format_exc()


def create_front_request(master_request, pageset):
    path = master_request.route_path("front", page_name=pageset.url) ##
    request = _make_request(urllib.unquote(path))
    request.matchdict = {}
    request._pageset = pageset
    request.matchdict["page_name"] = pageset.url
    return request

def collect_pageset(request):
    from altaircms.page.models import PageSet
    return request.registry.queryUtility(IAllowableQuery)(PageSet)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", 
                        help="Config file of app")
    args = parser.parse_args()
    return _main(args)

def _main(args):
    env = bootstrap(args.config)
    # setup_logging(args.config)
    logging_file_config(args.config)
    
    registry = env["registry"]
    request = env["request"]

    from pyramid.router import Router
    router = Router(registry)

    for pageset in collect_pageset(request)[5:]:
        request = create_front_request(request, pageset)
        check_rendering(router, request)

main()
