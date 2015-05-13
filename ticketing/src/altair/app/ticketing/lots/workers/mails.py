# -*- coding: utf-8 -*-
import logging
from pyramid.decorator import reify
from altair.sqlahelper import named_transaction
from altair.mq.decorators import task_config
from .election import ElectionWorkerResource
from .. import models as lot_models
from ..events import (
    LotElectedEvent,
    LotRejectedEvent,
    )
from ..models import (
    Lot,
    LotEntry,
    LotElectedEntry,
    LotRejectedEntry,
    )

logger = logging.getLogger(__name__)


class ElectionMailResource(object):
    def __init__(self, request):
        self.request = request
        self.lot_elected_entry_id = self.request.params.get('lot_elected_entry_id')

    @reify
    def lot_elected_entry(self):
        return LotElectedEntry.query.filter(LotElectedEntry.id == self.lot_elected_entry_id).first()

    @reify
    def lot_entry_wish(self):
        return self.lot_elected_entry.lot_entry_wish if self.lot_elected_entry else None

    @reify
    def lot_entry(self):
        return self.lot_entry_wish.lot_entry if self.lot_entry_wish else None

    @reify
    def lot(self):
        return self.lot_entry.lot if self.lot_entry else None


class RejectionMailResource(object):
    def __init__(self, request):
        self.request = request
        self.lot_rejected_entry_id = self.request.params.get('lot_rejected_entry_id')

    @reify
    def lot_rejected_entry(self):
        return LotRejectedEntry \
            .query \
            .join(LotEntry) \
            .join(Lot) \
            .filter(LotRejectedEntry.id == self.lot_rejected_entry_id) \
            .first()

    @reify
    def lot_entry(self):
        return self.lot_rejected_entry.lot_entry if self.lot_rejected_entry else None

    @reify
    def lot(self):
        return self.lot_entry.lot if self.lot_entry else None


@task_config(
    root_factory=ElectionMailResource,
    consumer='lots.election_mail',
    queue='lots.election_mail',
    timeout=600,
    )
def send_election_mail_task(context, request):
    with named_transaction(request, "lot_work_history") as s:
        history = lot_models.LotWorkHistory(
            lot_id=context.lot.id,  # 別トランザクションなのでID指定
            entry_no=context.lot_entry.entry_no,
            wish_order=context.lot_entry_wish.wish_order
            )
        s.add(history)

        try:
            logger.info("start send election mail: lot_id={lot_id}".format(lot_id=context.lot.id))
            if context.lot is None:
                logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
                return
            request.session['order'] = {'order_no': context.lot_entry.entry_no}
            wish = context.lot_entry_wish
            event = LotElectedEvent(request, wish)
            request.registry.notify(event)
        except Exception as e:
            history.error = str(e).decode('utf-8')
            raise


@task_config(
    root_factory=RejectionMailResource,
    consumer='lots.rejection_mail',
    queue='lots.rejection_mail',
    timeout=600,
    )
def send_rejection_mail_task(context, request):
    with named_transaction(request, "lot_work_history") as s:
        history = lot_models.LotWorkHistory(
            lot_id=context.lot.id,  # 別トランザクションなのでID指定
            entry_no=context.lot_entry.entry_no,
            )
        s.add(history)

        try:
            logger.info("start send election mail: lot_id={lot_id}".format(lot_id=context.lot.id))
            if context.lot is None:
                logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
                return
            request.session['order'] = {'order_no': context.lot_entry.entry_no}
            event = LotRejectedEvent(request, context.lot_entry)
            request.registry.notify(event)
        except Exception as e:
            history.error = str(e).decode('utf-8')
            raise
