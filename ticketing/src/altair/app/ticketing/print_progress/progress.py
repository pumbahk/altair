# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)

from collections import namedtuple
ProgressData = namedtuple("ProgressData", "total printed unprinted")
from pyramid.decorator import reify
from altair.app.ticketing.core.models import Event, Performance

class PrintProgressGetter(object):
    def __init__(self, request, organization):
        self.request = request
        self.organization = organization

    def get_event_progress(self, event):
        return DummyPrintProgress()

    def get_performance_progress(self, performance):
        return DummyPrintProgress()

class DummyPrintProgress(object):
    @reify
    def total(self):
        return 300

    @property
    def size(self):
        return 3

    @reify
    def qr(self):
        return ProgressData(total=100, printed=40, unprinted=60)

    @reify
    def shipping(self):
        return ProgressData(total=100, printed=100, unprinted=0)

    @reify
    def other(self):
        return ProgressData(total=20, printed=19, unprinted=1)
