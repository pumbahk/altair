# -*- coding: utf-8 -*-

from argparse import ArgumentParser
import logging
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy import orm
import sqlahelper
from .models import (
    PriceBatchUpdateTask,
    PriceBatchUpdateTaskStatusEnum
)
from .updater import run_price_batch_update_task

logger = logging.getLogger(__name__)


def do_price_batch_update():
    parser = ArgumentParser()
    parser.add_argument('--config', type=str, required=True)
    parser.add_argument('--task-ids', type=str, required=False) # for debug

    options = parser.parse_args()
    setup_logging(options.config)
    bootstrap(options.config)

    if options.task_ids:
        logger.info('argument: task_ids={}'.format(options.task_ids))

    logging.info('Start price batch update')
    # altair.app.ticketing.models.DBSession出ない場合はLogicallyDeletedが効かないことに注意
    session = orm.session.Session(bind=sqlahelper.get_engine())

    option_task_ids = map(int, options.task_ids.split(',')) if options.task_ids else []
    task_ids = []

    try:
        query = session.query(PriceBatchUpdateTask).filter(
            PriceBatchUpdateTask.status == PriceBatchUpdateTaskStatusEnum.Waiting.v,
            PriceBatchUpdateTask.deleted_at.is_(None)
        ).order_by(PriceBatchUpdateTask.id).with_lockmode('update')

        if option_task_ids:
            query.filter(PriceBatchUpdateTask.id.in_(option_task_ids))

        tasks = query.all()

        for task in tasks:
            task_ids.append(task.id)
            task.status = PriceBatchUpdateTaskStatusEnum.Updating.v

        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()

    logging.info('Running price batch tasks = [{}]'.format(task_ids))
    for task_id in task_ids:
        run_price_batch_update_task(task_id)

    logging.info('End price batch update')
