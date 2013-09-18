# -*- coding: utf-8 -*-

class EventHelper(object):
    def get_performance_start(self, event):
        min = None
        for perf in event.performances:
            if min:
                if perf.start_on < min:
                    min = perf.start_on
            else:
                min = perf.start_on
        return min

    def get_performance_end(self, event):
        max = None
        for perf in event.performances:
            if max and perf.end_on is not None:
                if perf.end_on > max:
                    max = perf.end_on
            else:
                max = perf.end_on

        if max is None:
            max = ""
        return max

    def get_deal_start(self, event):
        min = None
        for segment in event.sales_segments:
            if min:
                if segment.start_at < min:
                    min = segment.start_at
            else:
                min = segment.start_at
        return min

    def get_deal_end(self, event):
        max = None
        for segment in event.sales_segments:
            if max and segment.end_at is not None:
                if segment.end_at > max:
                    max = segment.end_at
            else:
                max = segment.end_at

        if max is None:
            max = ""
        return max
