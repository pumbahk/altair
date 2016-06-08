# -*- coding:utf-8 -*-


""" mqワーカー
"""
import transaction
import logging

from pyramid.decorator import reify

from altair.app.ticketing.payments.payment import Payment
from altair.mq.decorators import task_config
from altair.sqlahelper import named_transaction

from altair.app.ticketing.models import DBSession

from altair.app.ticketing.orders import models as order_models
from altair.app.ticketing.cart import models as cart_models
from altair.app.ticketing.cart import api as cart_api

from .. import models as lot_models
from ..events import LotRejectedEvent
from altair.app.ticketing.lots.models import (
    Lot
)

from altair.app.ticketing.payments.api import (
    is_finished_payment,
    is_finished_delivery,
)

logger = logging.getLogger(__name__)

# 当選処理
class RejectionWorkerResource(object):
    def __init__(self, request):
        self.request = request
        self.lot_id = self.request.params.get('lot_id')
        self.entry_no = self.request.params.get('entry_no')

    @reify
    def lot(self):
        return lot_models.Lot.query.filter(lot_models.Lot.id==self.lot_id).first()

    @reify
    def work(self):
        return lot_models.LotRejectWork.query.filter(
            lot_models.LotRejectWork.lot_entry_no == self.entry_no
        ).first()


@task_config(root_factory=RejectionWorkerResource,
             name="lots.rejection",
             consumer="lots.rejection",
             queue="lots.rejection",
             timeout=600)
def reject_lots_task(context, request):
    with named_transaction(request, "lot_work_history") as s:
        if not context.work:
            logger.info("nothing rejecting task: lot_id={lot_id}, entry_no={entry_no}".format(lot_id=context.lot.id, entry_no=context.entry_no))
            return

        history = lot_models.LotWorkHistory(
            lot_id=context.lot.id, # 別トランザクションなのでID指定
            entry_no=context.work.lot_entry_no,
            wish_order=None # wish_order = None => 落選
            )
        s.add(history)
        try:
            logger.info("start rejecting task: lot_id={lot_id}, work_id={work_id}".format(lot_id=context.lot.id, work_id=context.work.id))
            if context.lot is None:
                logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
                return

            lot_entry = context.work.lot_entry
            lot_entry.reject()
            DBSession.delete(context.work)
        except Exception as e:
            work = s.query(lot_models.LotRejectWork).filter_by(id=context.work.id).one()
            history.error = work.error = str(e).decode('utf-8')
            raise
