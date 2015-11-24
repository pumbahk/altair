# -*- coding:utf-8 -*-

from itertools import groupby
from urlparse import urljoin
from altaircms.helpers.link import get_link_from_topic
from altaircms.linklib import add_params_to_url
from altair.pyramid_assets import get_resolver
import json
import re

def resolve_url(url):
    pat = re.compile('s3://([^/]+)/(.*)')
    match = pat.match(url)
    if match:
        return 'http://%s.s3.amazonaws.com/%s' % (match.group(1), match.group(2))
    return url

class TopPageResponseBuilder(object):
    def _complete_url(self, request, url):
        if not url.startswith("http://") and not url.startswith("https://"):
            url = urljoin(request.host_url, url)
        return url

    def build_response(self, request, topcontents, topics):
        res = dict()
        res["topcontents"] = []
        res["topics"] = []
        for tc in topcontents:
            tcdict = dict()
            tcdict["title"] = tc.title
            tcdict["copy_text"] = tc.text
            tcdict["detail_url"] = get_link_from_topic(request, tc)
            tcdict["detail_url"] = self._complete_url(request, tcdict["detail_url"])
            if tc.trackingcode:
                params = {"l-id": tc.trackingcode}
                tcdict["detail_url"] = add_params_to_url(tcdict["detail_url"], params)
            tcdict["image_url"] = resolve_url(tc.image_asset.file_url) if tc.image_asset else None
            res["topcontents"].append(tcdict)
        for t in topics:
            tdict = dict()
            tdict["text"] = t.text
            tdict["detail_url"] = get_link_from_topic(request, t)
            tdict["detail_url"] = self._complete_url(request, tdict["detail_url"])
            if t.trackingcode:
                params = {"l-id": t.trackingcode}
                tdict["detail_url"] = add_params_to_url(tdict["detail_url"], params)
            res["topics"].append(tdict)

        return res

class GenreListResponseBuilder(object):
    def build_response(self, request, genres):
        res = {}

        for g in genres:
            if g.origin is None:
                if not res.has_key("origin"):
                    res["origin"] = []
                res["origin"].append({"id": g.id, "name": g.name, "label": g.label})
            else:
                if not res.has_key(g.origin):
                    res[g.origin] = []
                res[g.origin].append({"id": g.id, "name": g.name, "label": g.label})

        return res


class BaseListResponseBuilder(object):
    def _make_performance_list(self, performances):
            plist = []
            for p in performances:
                pdict = dict()
                pdict["id"] = p.id
                pdict["name"] = p.title
                pdict["open"] = p.start_on.strftime("%Y-%m-%d %H:%M:%S") if p.start_on else None
                pdict["close"] = p.end_on.strftime("%Y-%m-%d %H:%M:%S") if p.end_on else None
                pdict["venue"] = p.venue
                pdict["prefecture"] = p.prefecture
                pdict["sales_segments"] = self._make_sales_segment_list(p)
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

        sorted(performances, key=lambda x: x.event_id)
        for k, g in groupby(performances, key=lambda x: x.event_id):
            pglist.append(list(g))

        return pglist

    def build_response(self, request, performances):
        res = {"events": []}

        pgroups = self._grouping_performances(performances)

        for pg in pgroups:
            edict = dict()
            edict["event_id"] = pg[0].event_id
            edict["event_name"] = pg[0].event.title
            edict["performances"] = self._make_performance_list(pg)
            res["events"].append(edict)
        return res


class EventDetailResponseBuilder(BaseListResponseBuilder):
    def build_response(self, request, event, widget_summary):
        res = dict()
        res['event_id'] = event.id
        res['title'] = event.title
        res['subtitle'] = event.subtitle
        res['display_items'] = json.loads(widget_summary.items) if widget_summary is not None else [ ]
        res['performances'] = self._make_performance_list(event.performances)

        return res
