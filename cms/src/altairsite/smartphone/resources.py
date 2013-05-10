# -*- coding:utf-8 -*-
from datetime import datetime
from sqlalchemy import asc
from altaircms.topic.models import TopicTag, PromotionTag, TopcontentTag
from altaircms.topic.api import get_topic_searcher
from altaircms.models import Genre
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from altairsite.smartphone.common.const import get_areas

class GenreNode(object):
    def __init__(self, genre, children):
        self.genre = genre
        self.children = children

class TopPageResource(object):
    def __init__(self, request):
        self.request = request

    def get_system_tag_label(self, request, system_tag_id):
        if not system_tag_id:
            return None
        system_tag = request.allowable(Genre).filter(Genre.id==system_tag_id).first()
        return system_tag.label

    def _getInfo(self, searcher, tag, system_tag_label):
        if system_tag_label:
            system_tag = searcher.get_tag_from_genre_label(system_tag_label)
            results = searcher.query_publishing_topics(datetime.now(), tag, system_tag)
        else:
            results = searcher.query_publishing_topics(datetime.now(), tag)
        return results

    def getInfo(self, kind, system_tag_id):
        if kind == "promotion":
            searcher = get_topic_searcher(self.request, "promotion")
            tag = self.request.allowable(PromotionTag).filter_by(label=u"プロモーション枠").first()
        elif kind == "topcontent":
            searcher = get_topic_searcher(self.request, "topcontent")
            tag = self.request.allowable(TopcontentTag).filter_by(label=u"注目のイベント").first()
        elif kind == "topic":
            searcher = get_topic_searcher(self.request, "topic")
            tag = self.request.allowable(TopicTag).filter_by(label=u"トピックス").first()
        system_tag_label = self.get_system_tag_label(request=self.request, system_tag_id=system_tag_id)
        return self._getInfo(searcher=searcher, tag=tag, system_tag_label=system_tag_label)

    def get_hotword(self):
        today = datetime.now()
        hotwords = self.request.allowable(HotWord).filter(HotWord.term_begin <= today).filter(today <= HotWord.term_end) \
                 .filter_by(enablep=True).order_by(asc("display_order"), asc("term_end"))
        return hotwords

    def get_genre_tree(self, parent):
        genre_searcher = GenreSearcher(self.request)
        tree = genre_searcher.root.children
        if parent:
            tree = genre_searcher.get_children(parent)

        genretree = []
        for genre in tree:
            subgenre = genre_searcher.get_children(genre)
            node = GenreNode(genre=genre, children=subgenre)
            genretree.append(node)
        return genretree

    def get_area(self):
        return get_areas()
