# -*- coding:utf-8 -*-

from itertools import groupby
from urlparse import urljoin
from urlparse import urlparse
from altaircms.helpers.link import get_link_from_topic
from altaircms.linklib import add_params_to_url
from altair.pyramid_assets import get_resolver
from .helpers import (
    get_lot_id_from_url,
    is_performance_on_sale
)
import json
import re

import logging
logger = logging.getLogger(__name__)

def resolve_url(url):
    pat = re.compile('s3://([^/]+)/(.*)')
    match = pat.match(url)
    if match:
        return 'http://%s.s3.amazonaws.com/%s' % (match.group(1), match.group(2))
    return url


def build_detail_url(request, topic):
    url = get_link_from_topic(request, topic)
    pc_search_path = request.route_path('page_search_by_freeword')
    sp_search_path = request.route_path('smartphone.search')

    # SPリンク化
    if pc_search_path in url:
        url = url.replace(pc_search_path, sp_search_path)
        url = url.replace('?q=', '?word=')

    # host名がデータとリクエストで相違する場合は合わせる
    if not url.startswith(request.host_url):
        # データがpathの場合はホスト名を補完する
        if not urlparse(url).hostname:
            url = urljoin(request.host_url, url)
        else:
            url = urlparse(url)._replace(scheme=u"http").geturl()
            url = urlparse(url)._replace(netloc=request.host).geturl()

    # トラッキングコードクエリ追加
    if topic.trackingcode:
        params = {"l-id": topic.trackingcode}
        url = add_params_to_url(url, params, parse_qs_opts={ "keep_blank_values": True })

    return url

class TopPageResponseBuilder(object):
    def build_response(self, request, topcontents, topics):
        res = dict()
        res["topcontents"] = []
        res["topics"] = []
        for tc in topcontents:
            tcdict = dict()
            tcdict["title"] = tc.title
            tcdict["copy_text"] = tc.text
            tcdict["detail_url"] = build_detail_url(request, tc)
            tcdict["image_url"] = resolve_url(tc.image_asset.file_url) if tc.image_asset else None
            res["topcontents"].append(tcdict)
        for t in topics:
            tdict = dict()
            tdict["text"] = t.text
            tdict["detail_url"] = build_detail_url(request, t)
            res["topics"].append(tdict)

        return res

class GenreListResponseBuilder(object):
    def build_response(self, request, genres):
        res = {}
        for g in genres:
            if g.origin is None:
                if not res.has_key("origin"):
                    res["origin"] = []
                ancestors = g.ancestors
                res["origin"].append({"id": g.id,
                                      "name": g.name,
                                      "label": g.label,
                                      "parent_id": None,
                                      "hierarchy": len(ancestors)})
            else:
                if not res.has_key(g.origin):
                    res[g.origin] = []
                ancestors = g.ancestors
                parent_id = ancestors[0].id if ancestors else None
                # mm...ジャンルツリーに組み込まれていない奴がたまにいる
                if ancestors:
                    res[g.origin].append({"id": g.id,
                                          "name": g.name,
                                          "label": g.label,
                                          "parent_id": parent_id,
                                          "hierarchy": len(ancestors)})

        return res


class BaseListResponseBuilder(object):
    def _make_performance_list(self, request, performances):
            plist = []
            if performances is None:
                return plist
            for p in performances:
                pdict = dict()
                pdict["id"] = str(p.id) if p.id else None
                pdict["backend_id"] = str(p.backend_id) if p.backend_id else None
                pdict["name"] = p.title
                pdict["open"] = p.start_on.strftime("%Y-%m-%d %H:%M:%S") if p.start_on else None
                pdict["close"] = p.end_on.strftime("%Y-%m-%d %H:%M:%S") if p.end_on else None
                pdict["venue"] = p.venue
                pdict["prefecture"] = p.prefecture
                pdict["sales_segments"] = self._make_sales_segment_list(p)
                pdict["lot_id"] = get_lot_id_from_url(p.purchase_link)
                pdict["on_sale"] = is_performance_on_sale(p, request.now)
                plist.append(pdict)

            return plist

    def _make_sales_segment_list(self, performance):
        saleslist = []
        for ss in performance.sales:
            ssdict = dict()
            ssdict["name"] = ss.group.name
            ssdict["sales_start"] = ss.start_on.strftime("%Y-%m-%d %H:%M:%S") if ss.start_on else None
            ssdict["sales_end"] = ss.end_on.strftime("%Y-%m-%d %H:%M:%S") if ss.end_on else None
            saleslist.append(ssdict)

        return saleslist


class PerformanceGroupListResponseBuilder(BaseListResponseBuilder):
    def _grouping_performances(self, performances):
        ''' performanceをevent_id毎にグルーピングする '''
        pglist = []

        performances.sort(key=lambda x: x.event_id)
        for k, g in groupby(performances, key=lambda x: x.event_id):
            pglist.append(list(g))

        return pglist

    def build_response(self, request, events, page_count):
        res = {"page_count": page_count, "events": []}

        for event in events:
            edict = dict()
            edict["event_id"] = str(event.id) if event.id else None
            edict["backend_id"] = str(event.backend_id) if event.backend_id else None
            edict["title"] = event.title
            edict["performances"] = self._make_performance_list(request, event.performances)
            res["events"].append(edict)
        return res


class EventDetailResponseBuilder(BaseListResponseBuilder):
    def build_response(self, request, event, performances, event_info):
        pagesets = event.pagesets
        res = dict()
        res['event_id'] = str(event.id) if event.id else None
        res['backend_id'] = str(event.backend_id) if event.backend_id else None
        res['title'] = event.title
        res['subtitle'] = event.subtitle
        res['page_paths'] = [pageset.url for pageset in pagesets]
        res['genre_id'] = pagesets[0].genre_id if pagesets else None
        res['display_items'] = event_info["event"] if event_info else [ ]
        res['performances'] = self._make_performance_list(request, performances)

        return res
