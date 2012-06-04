from collections import defaultdict
from datetime import datetime, timedelta
import itertools

from altaircms.models import Performance
from altaircms.event.models import Event

class ParsedEvent(dict):
    def _parse_date(self, dt, default=None):
        """2012/06/14 -> datetime"""
        try:
            return datetime.strptime(dt, "%Y/%m/%d")
        except ValueError:
            try:
                m, d = [int(x) for x in dt.split("/")]
                return datetime(default.year, m, d)
            except:
                return default
            

    def __init__(self, args):
        self.pid, self.event_name, self.venue, self.event_open, self.event_close = (x.decode("utf-8") for x in args)

        self.pid = int(self.pid)
        self.event_open = self._parse_date(self.event_open)
        self.event_close = self._parse_date(self.event_close, self.event_open)

class Reducer(object):
    created_at = datetime(1900, 1, 1)

    def __init__(self):
        self.events = {}
        self.perfs = defaultdict(list)

    def create_event(self, src):
        return Event(
            title=src.event_name, 
            subtitle=src.event_name + "(subtitle)", 
            backend_id = src.pid,  ##?
            created_at = self.created_at, 
            event_open = src.event_open, 
            event_close = src.event_close)

    def update_event(self, ev, src):
        if ev.event_open > src.event_open:
            ev.event_open = src.event_open

        if ev.event_close < src.event_close:
            ev.event_close = src.event_close
        return ev
            
    def choice_event(self, src):
        if src.event_name not in self.events:
            ev = self.create_event(src)
        else:
            ev =  self.update_event(self.events[src.event_name], src)

        ev.deal_open = ev.event_open - timedelta(days=30)
        ev.deal_close = ev.event_close

        self.events[src.event_name] = ev

    def create_perf(self, src):
        return Performance(
            title=src.event_name, 
            venue=src.venue, 
            created_at = self.created_at, 
            open_on = src.event_open, 
            start_on = src.event_open, 
            end_on = src.event_close)

    def choice_perf(self, src):
        self.perfs[src.event_name].append(self.create_perf(src))

    def do(self, src): #rename
        self.choice_event(src)
        self.choice_perf(src)

import csv

"""
setup
"""
import altaircms.page.models
import sqlahelper
import sqlalchemy as sa

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--dburl")
parser.add_argument("--infile")
args = parser.parse_args()

sqlahelper.add_engine(sa.create_engine(args.dburl))
sqlahelper.get_base().metadata.create_all()
session = sqlahelper.get_session()
from altaircms.scripts.pmain.dump_as_csv import query_dump_as_csv

with open(args.infile) as rf:
    reader = csv.reader(rf)
    reducer = Reducer()

    for row in reader:
        reducer.do(ParsedEvent(row))

    session.add_all(reducer.events.values())
    session.flush()

    with open("events.csv", "w") as wf:
        query_dump_as_csv(Event, reducer.events.values(), wf, noid=True)

    with open("performances.csv", "w") as wf:
        perfs = itertools.chain.from_iterable(reducer.perfs.values())
        query_dump_as_csv(Performance, perfs, wf, noid=True)
