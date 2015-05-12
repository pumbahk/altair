# -*- coding: utf-8 -*-
import logging
from altair.sqlahelper import named_transaction
from altair.mq.decorators import task_config

from .election import ElectionWorkerResource
from .. import models as lot_models
from ..events import LotElectedEvent

logger = logging.getLogger(__name__)


@task_config(
    root_factory=ElectionWorkerResource,
    consumer='lots.send_election_mail',
    queue='lots.send_election_mail',
    timeout=600,
    )
def send_election_mail_task(context, request):
    with named_transaction(request, "lot_work_history") as s:
        history = lot_models.LotWorkHistory(
            lot_id=context.lot.id,  # 別トランザクションなのでID指定
            entry_no=context.work.lot_entry_no,
            wish_order=context.work.wish_order
            )
        s.add(history)

        try:
            logger.info("start send election mail: lot_id={lot_id}, work_id={work_id}".format(
                lot_id=context.lot.id, work_id=context.work.id))
            if context.lot is None:
                logger.warning("lot is not found: lot_id = {0}".format(context.lot_id))
                return
            request.session['order'] = {'order_no': context.work.lot_entry_no}
            wish = context.work.wish
            event = LotElectedEvent(request, wish)
            request.registry.notify(event)
        except Exception as e:
            work = s.query(lot_models.LotElectWork).filter_by(id=context.work.id).one()
            history.error = work.error = str(e).decode('utf-8')
            raise
