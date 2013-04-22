# -*- encoding:utf-8 -*-

"""
csvのformat

organization_id, layout_id, genre_id
organization_id, layout_id, genre_id
organization_id, layout_id, genre_id
...
"""
import json
import sys
from datetime import datetime
import csv
import logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARN)
import argparse
import transaction
from pyramid.paster import bootstrap

def main():
    parser = argparse.ArgumentParser(description="register category top page", formatter_class=argparse.RawDescriptionHelpFormatter,)
    parser.add_argument("config", help=u"development.ini'")
    parser.add_argument("operator_id", type=int)
    parser.add_argument('infile', help=u"csv file", nargs='?', type=argparse.FileType('r'),
                         default=sys.stdin)
    parser.add_argument("--verbose", default=False, action="store_const", const=bool)
    args = parser.parse_args()
    _main(args)

created_pages = []
def set_created_page(self):
    if created_pages:
        created_pages.pop(0)
    created_pages.append(self.obj)

def get_created_page():
    return created_pages[0]
    
def _main(args):
    try:
        env = bootstrap(args.config)
        from altaircms.page.subscribers import PageCreate
        registry = env["registry"]
        registry.registerHandler(set_created_page, (PageCreate, ))

        from altaircms.security import OverrideAuthenticationPolicy
        from pyramid.interfaces import IAuthenticationPolicy
        registry.registerUtility(OverrideAuthenticationPolicy(args.operator_id), IAuthenticationPolicy)
        run(env, args.infile)
        transaction.commit()
    except Exception, e:
        logger.exception(str(e))
        transaction.abort()

def get(qs):
    return qs.one()


def create_page(env, organization_id, layout, genre):
    from altaircms.page.resources import PageResource
    from altaircms.page.views import PageAddView
    from altaircms.testing import ExtDummyRequest
    from altaircms.page.models import PageDefaultInfo
    pdi = get(PageDefaultInfo.query.filter_by(pagetype_id=layout.pagetype_id))
    info = pdi.get_page_info(layout.pagetype, genre, None)
    params = {
        "name": info.name, 
        "caption": info.caption, 
        "title_prefix": info.title_prefix,
        "title": info.title,
        "title_suffix": info.title_suffix,
        "event": None, 
        "url": info.url.lstrip("/") if not info.url.startswith(("http://", "https://")) else info.url, 
        "genre": unicode(genre.id), 
        "keywords": info.keywords, 
        "description": info.description, 
        "publish_begin": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")), 
        "layout": unicode(layout.id), 
        "pagetype": unicode(layout.pagetype.id), 
        }
    request = ExtDummyRequest(organization_id=organization_id, POST=params, current_request=True)
    context = PageResource(request)
    view = PageAddView(context, request)
    view.create_page()
    sys.stderr.write(".")
    return get_created_page()

def run(env, csvfile):
    from altaircms.layout.models import Layout
    from altaircms.models import Genre
    import transaction

    for organization_id, layout_id, genre_id in csv.reader(csvfile):
        try:
            genre = get(Genre.query.filter_by(id=genre_id))
            if genre.category_top_pageset_id:
                logger.warn("skip: genre %s layout %s organization %s" % (genre.id, layout_id, organization_id))
                continue
            layout = get(Layout.query.filter_by(id=layout_id))
            create_page(env, organization_id, layout, genre)
            transaction.commit()
        except Exception, e:
            logger.exception(e)
            logger.warn("error: genre %s layout %s organization %s" % (genre_id, layout_id, organization_id))
            break

if __name__ == "__main__":
    main()
