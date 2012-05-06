from pyramid import testing
import altaircms.helpers as h

def main(env, args):
    request = testing.DummyRequest()
    class PageSet(object):
        url = "foo"
    print h.front.to_publish_page_from_pageset(request, PageSet)


    
