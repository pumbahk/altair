# -*- coding: utf-8 -*-

import logging
from sqlahelper import get_engine
from sqlalchemy.orm import session
from sqlalchemy.orm.exc import NoResultFound

from pyramid.decorator import reify

from altair.app.ticketing.orders import models as order_models
logger = logging.getLogger(__name__)


class ImportPerOrderResource(object):
    def __init__(self, request):
        self._session = session.Session(bind=get_engine())
        self.request = request
        self.proto_order_id = self.request.params.get('proto_order_id')
        self.entrust_separate_seats = self.request.params.get('entrust_separate_seats')

    @reify
    def proto_order(self):

        try:
            return order_models.ProtoOrder.filter_by(id=self.proto_order_id).one()
        except NoResultFound:
            return None


class ImportPerTaskResource(object):
    def __init__(self, request):
        self._session = session.Session(bind=get_engine())
        self.request = request
        self.order_import_task_id = self.request.params.get('order_import_task_id')

    @reify
    def order_import_task(self):
        try:
            return order_models.OrderImportTask.query.filter_by(id=self.order_import_task_id).one()
        except NoResultFound:
            return None