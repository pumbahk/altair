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

import functools

class TransactionWrapper(object):
    def __init__(self, o):
        self.o = o
    def __getattr__(self, k):
        return getattr(self.o, k)

    def get_tag_from_genre_label(self, name):
        stag = self.o.get_tag_from_genre_label(name)
        if stag.id is None:
            from altaircms.models import DBSession
            import transaction
            DBSession.add(stag)
            DBSession.flush()
            transaction.commit()
            stag = DBSession.merge(stag)
        assert stag.id
        return stag

class CategoryPageBlocksBuilder(object):
    def __init__(self, env):
        self.env = env
        from altaircms.topic.api import get_topic_searcher
        from altaircms.page.api import get_pageset_searcher
        request = self.env["request"]
        self.topic_searcher = TransactionWrapper(get_topic_searcher(request, "topic"))
        self.topcontent_searcher = TransactionWrapper( get_topic_searcher(request, "topcontent"))
        self.promotion_searcher = TransactionWrapper(get_topic_searcher(request, "promotion"))
        self.pageset_searcher = TransactionWrapper(get_pageset_searcher(request))

    def build(self, page, genre):
        blocks = {}
        blocks["main"] = self.build_main(page,genre)
        blocks["main_left"] = self.build_main_left(page,genre)
        blocks["main_right"] = self.build_main_right(page,genre)
        blocks["main_bottom"] = self.build_main_bottom(page,genre)
        blocks["side"] = self.build_side(page,genre)
        return blocks

    def build_main(self, page, genre):
        from altaircms.topic.models import TopicTag
        from altaircms.topic.models import TopcontentTag
        from altaircms.topic.models import PromotionTag
        r = []
        add = self._create_add_widget_function(page, genre, r)
        allowable = lambda m: m.query.filter_by(organization_id=page.organization_id)
        add("topic", {"tag": allowable(TopicTag).filter_by(label=u"特集").one().id, 
                      "system_tag": "__None" if genre.origin is None else self.topic_searcher.system_tagmanager.get_or_create_tag(genre.origin_genre.label, public_status=True).id, 
                      "display_type": "topic", 
                      "display_count": 2})
        add("promotion", {"tag": allowable(PromotionTag).filter_by(label=u"プロモーション枠").one().id, 
                          "system_tag": self.promotion_searcher.get_tag_from_genre_label(genre.label).id, 
                          "display_type": "tstar_category_top"})
        add("heading", {"kind": u"{0}_heading".format(genre.origin or genre.name), 
                        "text": u"トピックス"
                        })
        add("topic", {"tag": allowable(TopicTag).filter_by(label=u"トピックス").one().id, 
                      "system_tag": self.topic_searcher.get_tag_from_genre_label(genre.label).id, 
                      "display_type": "topic", 
                      "display_count": 10})
        add("heading", {"kind": u"{0}_heading".format(genre.origin or genre.name), 
                        "text": u"注目のイベント"
                        })
        add("topcontent", {"tag": allowable(TopcontentTag).filter_by(label=u"注目のイベント").one().id, 
                           "system_tag": self.topcontent_searcher.get_tag_from_genre_label(genre.label).id, 
                           "rendering_image_attribute": "thumbnail_path", 
                           "display_type": "notable_event", 
                           "display_count": 8})
        return r

    def build_main_left(self, page, genre):
        r = []
        add = self._create_add_widget_function(page, genre, r)

        add("heading", {"kind": u"{0}_heading".format(genre.origin or genre.name), 
                        "text": u"今週販売のチケット"
                        })
        add("linklist", {
                "finder_kind": "thisWeek", 
                "delimiter": u"/", 
                "max_items": "20", 
                "limit_span":u"7", 
                "system_tag": self.pageset_searcher.get_tag_from_genre_label(genre.label).id, 
                })
        return r

    def build_main_right(self, page, genre):
        r = []

        add = self._create_add_widget_function(page, genre, r)
        add("heading", {"kind": u"{0}_heading".format(genre.origin or genre.name), 
                        "text": u"販売終了間近"
                        })
        add("linklist", {
                "finder_kind": "nearTheEnd", 
                "delimiter": u"/", 
                "max_items": "10", 
                "limit_span":u"7", 
                "system_tag": self.pageset_searcher.get_tag_from_genre_label(genre.label).id, 
                })
        return r

    def build_main_bottom(self, page, genre):
        return []

    def build_side(self, page, genre):
        from altaircms.topic.models import TopicTag
        r = []
        add = self._create_add_widget_function(page, genre, r)
        allowable = lambda m: m.query.filter_by(organization_id=page.organization_id)

        add("heading", {"kind": u"sidebar-heading", 
                        "text": u"特集"
                        })
        add("topic", {"tag": allowable(TopicTag).filter_by(label=u"特集").one().id, 
                      "system_tag": self.topic_searcher.get_tag_from_genre_label(genre.label).id, 
                      "display_type": "feature", 
                      "display_count": 5})
        return r

    def _create_add_widget_function(self, page, genre, r):
        from altaircms.plugins.widget.api import WidgetRegisterViewProxy as WP
        request = self.env["request"]
        wp = WP(request)
        return functools.partial(self.add_widget, wp, page, genre, r)
        
    def add_widget(self, wp, page, genre, r, name, params):
        from altaircms.models import DBSession
        try:
            response = wp.create(name, {"page_id": unicode(page.id), "data": params})
            data = response.json_body
            page = DBSession.merge(page)
            genre = DBSession.merge(genre)
            r.append({"name": name, "pk": data["pk"]})
        except (ValueError, KeyError):
            logger.error(response.body)
            raise 
        
    
def run(env, csvfile):
    from altaircms.layout.models import Layout
    from altaircms.models import Genre
    from altaircms.models import DBSession
    import transaction
    blocks_builder = CategoryPageBlocksBuilder(env)

    for organization_id, layout_id, genre_id in csv.reader(csvfile):
        try:
            genre = get(Genre.query.filter_by(id=genre_id))
            if genre.category_top_pageset_id:
                logger.warn("skip: genre %s layout %s organization %s" % (genre.id, layout_id, organization_id))
                continue
            layout = get(Layout.query.filter_by(id=layout_id))
            page = create_page(env, organization_id, layout, genre)
            transaction.commit()
            page = DBSession.merge(page)
            genre = DBSession.merge(genre)
            blocks = blocks_builder.build(page, genre)
            page.structure = json.dumps(blocks)
            DBSession.add(page)
        except Exception, e:
            logger.exception(e)
            logger.warn("error: genre %s layout %s organization %s" % (genre_id, layout_id, organization_id))
            break

if __name__ == "__main__":
    main()
