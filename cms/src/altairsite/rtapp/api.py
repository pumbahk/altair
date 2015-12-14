# -*- coding:utf-8 -*-

import logging
logger = logging.getLogger(__name__)

from sqlalchemy import or_
from altaircms.models import Performance, Genre, SalesSegment
from altaircms.event.models import Event
from altaircms.page.models import PageSet
from altaircms.topic.models import Promotion, TopicCore, Topic, Topcontent
from altaircms.plugins.widget.summary.models import SummaryWidget
from altaircms.helpers.search import escape_wildcard_for_like
from datetime import datetime as dt
import datetime

PREF_LIST = {
    "hokkaido": ["hokkaido"],
    "tohoku": ["aomori", "iwate", "miyagi", "akita", "yamagata", "fukushima"],
    "kitakanto": ["ibaraki", "tochigi", "gunma"],
    "shutoken": ["saitama", "chiba", "tokyo", "kanagawa", "yamanashi"],
    "chubu": ["niigata", "toyama", "ishikawa", "fukui", "yamanashi", "nagano", "gifu", "shizuoka", "aichi"],
    "koshinetsu": ["niigata", "nagano"],
    "hokuriku": ["toyama", "ishikawa", "fukui"],
    "tokai": ["shizuoka", "aichi", "gifu", "mie"],
    "kinki": ["osaka", "kyoto", "shiga", "hyogo", "nara", "wakayama"],
    "chugoku": ["tottori", "shimane", "okayama", "hiroshima", "yamaguchi"],
    "shikoku": ["tokushima", "kagawa", "ehime", "kouchi"],
    "kyushu": ["fukuoka", "saga", "nagasaki", "kumamoto", "oita", "miyazaki", "kagoshima", "okinawa"],
    "okinawa": ["okinawa"]
}

def get_promotions(session, request, now, organization_id):
    promotions = session.query(Promotion) \
                        .filter(Promotion.organization_id == organization_id,
                                Promotion.publish_open_on <= now,
                                Promotion.publish_close_on >= now,
                                Promotion.is_vetoed == 0
                                ) \
                        .order_by(Promotion.display_order)
    return promotions.all()

def get_topcontents(session, request, now, organization_id, limit=5):
    topcontents = session.query(Topcontent) \
                         .filter(Topcontent.organization_id == organization_id,
                                 Topcontent.publish_open_on <= now,
                                 Topcontent.publish_close_on >= now,
                                 Topcontent.is_vetoed == 0
                                 ) \
                         .order_by(Topcontent.display_order) \
                         .limit(limit)
    return topcontents.all()

def get_topics(session, request, now, organization_id, limit=5):
    topics = session.query(Topic) \
                    .filter(Topic.organization_id == organization_id,
                            Topic.publish_open_on <= now,
                            Topic.publish_close_on >= now,
                            Topic.is_vetoed == 0
                            ) \
                    .order_by(Topic.display_order) \
                    .limit(limit)
    return topics.all()

def get_genre_list(session, request, organization_id):
    genres = session.query(Genre).filter_by(organization_id=organization_id).all()
    return genres

def get_event(session, request):
    event_id = request.matchdict['event_id']
    event = session.query(Event).filter(Event.id == event_id).one()
    return event

def get_widget_summary(session, event):
    widget_summary = session.query(SummaryWidget).filter(SummaryWidget.bound_event_id == event.id).first()
    return widget_summary

def get_performance_list_query(session, request, organization_id):
    params = request.GET
    query = session.query(Performance) \
                   .join(Event, Performance.event_id == Event.id) \
                   .filter(Event.organization_id == organization_id) \
                   .filter(Performance.public == 1) \
                   .filter(or_(Performance.start_on >= dt.now(),
                               Performance.end_on >= dt.now())) \
                   .order_by(Performance.start_on) \
                   .group_by(Performance.id)

    # todo: paramsのフォーマットチェックが必要
    # キーワード検索
    if params.get('keyword'):
        esc_words = escape_wildcard_for_like(params.get('keyword'))
        cond = 'OR' if (params.get('keyword-op') == 'OR') else 'AND'
        if cond == 'AND':
            for keyword in esc_words.split():
                pattern = u'%{}%'.format(keyword)
                query = query.filter(or_(Performance.title.like(pattern, escape=u"\\"),
                                         Event.title.like(pattern, escape=u"\\"),
                                         Event.subtitle.like(pattern, escape=u"\\"),
                                         Event.description.like(pattern, escape=u"\\"),
                                         Event.notice.like(pattern, escape=u"\\"),
                                         Event.performers.like(pattern, escape=u"\\")))
        elif cond == 'OR':
            conditions = []
            for keyword in esc_words.split():
                pattern = u'%{}%'.format(keyword)
                conditions.append(Performance.title.like(pattern, escape="\\"))
                conditions.append(Event.title.like(pattern, escape=u"\\"))
                conditions.append(Event.subtitle.like(pattern, escape=u"\\"))
                conditions.append(Event.description.like(pattern, escape=u"\\"))
                conditions.append(Event.notice.like(pattern, escape=u"\\"))
                conditions.append(Event.performers.like(pattern, escape=u"\\"))

            query = query.filter(or_(*conditions))

    # 地域検索
    if params.get('area'):
        if params.get('area') in PREF_LIST.keys():
            query = query.filter(Performance.prefecture.in_(PREF_LIST[params.get('area')]))
        else:
            query = query.filter(Performance.prefecture == params.get('area'))

    # ジャンル検索
    if params.get('genre'):
        origin_genres = session.query(Genre).filter(Genre.organization_id == 8) \
                                            .filter('genre.origin is NULL') \
                                            .all()
        # クエリがorigin_genreである場合は、配下のジャンル全てで検索
        origin_genre = filter(lambda og: og.id == int(params.get('genre')), origin_genres)
        if origin_genre:
            query = query.join(PageSet, PageSet.event_id == Event.id) \
                         .join(Genre, Genre.id == PageSet.genre_id) \
                         .filter(or_(PageSet.genre_id == int(params.get('genre')),
                                     Genre.origin == origin_genre[0].name))
        else:
            query = query.join(PageSet, PageSet.event_id == Event.id) \
                         .filter(PageSet.genre_id == int(params.get('genre')))

    # 公演日検索
    if params.get('open') or params.get('close') or params.get('event_open_in'):
        # クエリ作成
        if params.get('open') and params.get('close'):
            prm_open = dt.strptime(params.get('open'), '%Y-%m-%d')
            prm_close = dt.strptime(params.get('close'), '%Y-%m-%d')
            prm_close = dt(prm_close.year, prm_close.month, prm_close.day, 23, 59, 59)
        elif params.get('open') and not params.get('close'):
            prm_open = dt.strptime(params.get('open'), '%Y-%m-%d')
            prm_close = dt(2100, 12, 31, 23, 59, 59)
        elif not params.get('open') and params.get('close'):
            prm_open = dt(1900, 1, 1, 0, 0, 0)
            prm_close = dt.strptime(params.get('close'), '%Y-%m-%d')
            prm_close = dt(prm_close.year, prm_close.month, prm_close.day, 23, 59, 59)
        elif params.get('event_open_in'):
            days = int(params.get('event_open_in'))
            prm_open = dt.now()
            prm_close = dt.now() + datetime.timedelta(days=days)
            prm_close = dt(prm_close.year, prm_close.month, prm_close.day, 23, 59, 59)

        query = query.filter(Performance.start_on >= prm_open,
                             Performance.start_on <= prm_close)

    # Todo: リファクタリング。条件が一緒にセットされるとまずいものがあるので、エラー出すとかする。
    # クエリ期間中に販売しているものを検索
    if params.get('sales_start') or params.get('sales_end'):
        # クエリ作成
        if params.get('sales_start') and params.get('sales_end'):
            prm_sales_start = dt.strptime(params.get('sales_start'), '%Y-%m-%d')
            prm_sales_end = dt.strptime(params.get('sales_end'), '%Y-%m-%d')
            prm_sales_end = dt(prm_sales_end.year, prm_sales_end.month, prm_sales_end.day, 23, 59, 59)
        elif params.get('sales_start') and not params.get('sales_end'):
            prm_sales_start = dt.strptime(params.get('sales_start'), '%Y-%m-%d')
            prm_sales_end = dt(2300, 12, 31, 23, 59, 59)
        elif not params.get('sales_start') and params.get('sales_end'):
            prm_sales_start = dt(1900, 1, 1, 0, 0, 0)
            prm_sales_end = dt.strptime(params.get('sales_end'), '%Y-%m-%d')
            prm_sales_end = dt(prm_sales_end.year, prm_sales_end.month, prm_sales_end.day, 23, 59, 59)

        query = query.join(SalesSegment, Performance.id == SalesSegment.performance_id) \
                     .filter(SalesSegment.start_on <= prm_sales_end,
                             SalesSegment.end_on >= prm_sales_start)

    if params.get('sales_start_in') or params.get('sales_end_in'):
        days = int(params.get('sales_start_in') or params.get('sales_end_in'))
        prm_term_start = dt.now()
        prm_term_end = dt.now() + datetime.timedelta(days=days)
        prm_term_end = dt(prm_term_end.year, prm_term_end.month, prm_term_end.day, 23, 59, 59)
        # 〜日以内に販売開始するものを検索
        if params.get('sales_start_in'):
            query = query.join(SalesSegment, Performance.id == SalesSegment.performance_id) \
                         .filter(SalesSegment.start_on >= prm_term_start,
                                 SalesSegment.start_on <= prm_term_end)
        # 〜日以内に販売終了するものを検索
        elif params.get('sales_end_in'):
            query = query.join(SalesSegment, Performance.id == SalesSegment.performance_id) \
                         .filter(SalesSegment.end_on >= prm_term_start,
                                 SalesSegment.end_on <= prm_term_end)

    # 販売期間クエリがない場合は販売中の条件を追加
    if not(params.get('sales_start') or params.get('sales_end') or
           params.get('sales_start_in') or params.get('sales_end_in')):
        query = query.join(SalesSegment, Performance.id == SalesSegment.performance_id) \
                     .filter(SalesSegment.end_on >= dt.now())

    return query


def get_bookmarked_performances(session, request, organization_id):
    params = request.GET
    query = None
    if params.get('bookmarks[]'):
        event_ids = params.get('bookmarks[]').split(',')
        query = session.query(Performance) \
                       .join(Event, Performance.event_id == Event.id) \
                       .filter(Event.organization_id == organization_id) \
                       .filter(Event.id.in_(event_ids)) \
                       .order_by(Performance.updated_at.desc()) \
                       .group_by(Performance.id)

    return query
