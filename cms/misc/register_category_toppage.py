# -*- encoding:utf-8 -*-

"""
csvのformat

organization_id, layout_id, genre_id
organization_id, layout_id, genre_id
organization_id, layout_id, genre_id
...
"""
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
    parser.add_argument('infile', help=u"csv file", nargs='?', type=argparse.FileType('r'),
                         default=sys.stdin)
    parser.add_argument("--verbose", default=False, action="store_const", const=bool)
    args = parser.parse_args()
    _main(args)

def _main(args):
    try:
        env = bootstrap(args.config)
        run(env, args.infile)
        transaction.commit()
    except Exception, e:
        logger.exception(str(e))
        transaction.abort()

def get(qs):
    return qs.one()


def run(env, csvfile):
    from altaircms.page.resources import PageResource
    from altaircms.page.views import PageAddView
    from altaircms.testing import ExtDummyRequest
    from altaircms.layout.models import Layout
    from altaircms.models import Genre
    from altaircms.page.models import PageDefaultInfo
    for organization_id, layout_id, genre_id in csv.reader(csvfile):
        genre = get(Genre.query.filter_by(id=genre_id))
        if genre.category_top_pageset_id:
            logger.warn("skip: genre %s layout %s organization %s" % (genre_id, layout_id, organization_id))
            continue
        layout = get(Layout.query.filter_by(id=layout_id))
        pdi = get(PageDefaultInfo.query.filter_by(pagetype_id=layout.pagetype_id))
        info = pdi.get_page_info(layout.pagetype, genre, None)
        params = {
            "name": info.name, 
            "caption": info.caption, 
            "title": info.title, 
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
        try:
            view = PageAddView(context, request)
            view.create_page()
            sys.stderr.write(".")
        except:
            logger.warn("error: genre %s layout %s organization %s" % (genre_id, layout_id, organization_id))

if __name__ == "__main__":
    main()
