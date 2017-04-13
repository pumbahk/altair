# -*- coding:utf-8 -*-


import logging
import json
from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from altaircms.modellib import DBSession
from sqlalchemy import or_, and_
from sqlalchemy.orm import joinedload, aliased
from ..event.models import Event
from ..models import Performance, Word, WordSearch, Performance_Word, Event_Word

from altair.viewhelpers.datetime_ import dt2str
logger = logging.getLogger(__file__)


@view_config(route_name="api_keyword", request_method="GET", renderer='json')
def api_word_get(request):
    cart_performance = request.params.get('backend_performance_id')
    if cart_performance:
        # performanceに紐づくものとeventに紐づくものの両方をマージして返す
        performance = request.allowable(Performance)\
            .options(joinedload(Performance.event))\
            .filter_by(backend_id=cart_performance)\
            .first()
        if performance is None:
            # no such performance
            return dict()

        w1 = request.allowable(Performance, DBSession.query(Performance_Word.word_id))\
        .filter(Performance_Word.performance_id == performance.id)

        w2 = request.allowable(Event, DBSession.query(Event_Word.word_id))\
        .filter(Event_Word.event_id == performance.event_id)

        words = words_by_ids(request, w1.union(w2)).all()

        event = dict(id=performance.event.id, title=performance.event.title)

        return dict(performance=dict(title=performance.title, event=event),
                    words=build_word_merge(words))

    cart_event = request.params.get('backend_event_id')
    if cart_event:
        # eventのに紐づくものだけを返す, performanceに紐づくwordは無視
        event = request.allowable(Event)\
            .filter_by(backend_id=cart_event)\
            .first()
        if event is None:
            # no such event
            return dict()

        w1 = request.allowable(Event, DBSession.query(Event_Word.word_id))\
        .filter(Event_Word.event_id == event.id)

        words = words_by_ids(request, w1).all()

        result = dict(event=dict(id=event.id, title=event.title),
                      words=build_word_merge(words))

        # ひとまず、これは常時True
        include_pages = True
        if include_pages:
            pages = list()
            for ps in event.pagesets:
                p = ps.current()
                if p is not None:
                    pages.append(dict(path=ps.url,
                                      page_id=p.id,
                                      publish_begin=p.publish_begin.isoformat() if p.publish_begin is not None else None,
                                      publish_end=p.publish_end.isoformat() if p.publish_end is not None else None,
                                      ))
            result['pages'] = pages

        # いまは使わなさそうなので、常時False
        include_performances = False
        if include_performances:
            performances = list()
            for p in event.performances:
                performances.append(dict(id=p.id, title=p.title))

            result['performances'] = performances

        return result

    id_list = request.params.get('id')
    if id_list is not None and 0 < len(id_list):
        # 廃止ワードのidであっても、hitさせて、統合ワードを返す
        id_list = id_list.split(' ')
        words = words_by_ids(request, id_list).all()
        return dict(words=build_word_merge(words))

    q = request.params.get('q')
    if q is not None and 0 < len(q):
        # 廃止ワードのlabelやそのsaerchは見ない（統合ワードだけを対象とする）
        words = words_by_keyword(request, q).all()
        return dict(words=build_word_merge(words))

    raise HTTPBadRequest()


def build_word_merge(tuples):
    """
    group by idして、_merge_word_id列をmerge[]に変換する

    :param tuples:
    :return:
    """
    words = dict()
    for word in tuples:
        if word.id not in words:
            words[word.id] = dict([ (k, v) for (k, v) in word.__dict__.items() if k[0]!='_' ])
            words[word.id]["merge"] = [ ]
        if word._merge_word_id is not None and word._merge_word_id not in words[word.id]["merge"]:
            words[word.id]["merge"].append(word._merge_word_id)

    return words.values()


def words_by_ids(request, ids):
    """
    親子関係があるとして、親idまたは子idにいずれかで検索した場合に、同一の結果が帰ってくる

    Word(id=1, merge_to_word_id=NULL)
    Word(id=2, merge_to_word_id=1)
    Word(id=3, merge_to_word_id=1)
    というレコードがあるとした場合、
    パラメータidsが[1]でも[2]でも[3]でも[1, 2]でも、結果は
    Word(id=1, merge: [2, 3])
    になる

    :param request:
    :param ids:
    :return:
    """
    index_word = aliased(Word)
    merge_word = aliased(Word)
    query = DBSession.query(Word.id, Word.label, Word.type, Word.label_kana, Word.description, merge_word.id.label('_merge_word_id'))
    return request.allowable(Word, query) \
        .outerjoin(index_word, or_(Word.id == index_word.merge_to_word_id, and_(Word.merge_to_word_id == None, Word.id == index_word.id))) \
        .filter(index_word.id.in_(ids)) \
        .filter(index_word.deleted_at == None) \
        .filter(Word.deleted_at == None) \
        .outerjoin(merge_word, and_(merge_word.merge_to_word_id == Word.id, merge_word.deleted_at == None)) \
        .distinct()


def words_by_keyword(request, q):
    """
    親のlabel、label_kana、親のWordSearchのみが検索対象（子は検索対象ではない）

    :param request:
    :param q:
    :return:
    """
    merge_word = aliased(Word)
    query = DBSession.query(Word.id, Word.label, Word.type, Word.label_kana, Word.description, merge_word.id.label('_merge_word_id'))
    return request.allowable(Word, query) \
        .filter(Word.deleted_at == None) \
        .filter(Word.merge_to_word_id == None) \
        .outerjoin(WordSearch, WordSearch.deleted_at == None) \
        .filter(or_(Word.label.contains(q), Word.label_kana.contains(q), WordSearch.data.contains(q))) \
        .outerjoin(merge_word, and_(merge_word.merge_to_word_id == Word.id, merge_word.deleted_at == None)) \
        .distinct()
