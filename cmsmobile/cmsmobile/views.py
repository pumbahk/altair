# coding:utf-8
from datetime import datetime
from pyramid.view import view_config
from altaircms.topic.models import TopicTag, PromotionTag
from altaircms.topic.api import get_topic_searcher
from altaircms.genre.searcher import GenreSearcher
from altaircms.tag.models import HotWord
from cmsmobile.forms import TopForm

@view_config(route_name='home', renderer='cmsmobile:templates/top/top.mako')
def main(request):

    form = TopForm()

    topic_searcher = get_topic_searcher(request, "topic")
    tag = TopicTag.query.filter_by(label=u"注目のイベント").first()
    if tag:
        form.attentions.data = topic_searcher.query_publishing_topics(datetime.now(), tag)[0:8]

    promo_searcher = get_topic_searcher(request, "promotion")
    tag = PromotionTag.query.filter_by().first()
    if tag:
        form.promotions.data = promo_searcher.query_publishing_topics(datetime.now(), tag)[0:5]

    tag = TopicTag.query.filter_by(label=u"トピック").first()
    if tag:
        form.topics.data = topic_searcher.query_publishing_topics(datetime.now(), tag)[0:5]

    form.hotwords.data = HotWord.query.filter(HotWord.organization_id == request.organization.id)\
        .filter(HotWord.enablep == True)\
        .filter(HotWord.term_begin < datetime.now())\
        .filter(datetime.now() < HotWord.term_end)\
        .order_by(HotWord.display_order)[0:5]

    genre_searcher = GenreSearcher(request)
    form.genretree.data = genre_searcher.root.children

    return {'form':form}
