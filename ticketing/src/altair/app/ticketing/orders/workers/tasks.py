# -*- coding: utf-8 -*-

import json
import logging
import re
import six
import sys
import transaction
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound

from altair.mq.decorators import task_config

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core.models import ChannelEnum
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.orders import api as orders_api
from altair.app.ticketing.orders import models as orders_models
from altair.app.ticketing.orders.exceptions import OrderCreationError, MassOrderCreationError

from .resources import (ImportPerOrderResource, ImportPerTaskResource)

logger = logging.getLogger(__name__)

def add_note(proto_order, order):
    note = re.split(ur'\r\n|\r|\n', order.note)
    # これは実時間でよいような
    imported_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    if proto_order.original_order is None or proto_order.order_no != proto_order.original_order.order_no:
        note.append(u'CSVファイル内の予約番号 (グループキー): %s' % proto_order.ref)
    note.append(u'インポート日時: %s' % imported_at)
    order.note = u'\n'.join(note)
    # 決済日時はコンビニ決済でないなら維持 (これは同じ処理を他でやっているはずなので必要ないかも)
    payment_plugin_id = order.payment_delivery_pair.payment_method.payment_plugin_id
    if payment_plugin_id != payments_plugins.SEJ_PAYMENT_PLUGIN_ID:
        order.paid_at = proto_order.new_order_paid_at



@task_config(root_factory=ImportPerOrderResource,
             name="import_per_order",
             consumer="import_per_order",
             queue="import_per_order",
             timeout=300,
             arguments={"maxPriority": 10})
def import_per_order(context, request):
    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)
    _now = datetime.now()
    try:
        _proto_order = context._session.query(orders_models.ProtoOrder).filter_by(id=context.proto_order_id).one()
    except NoResultFound:
        logger.error('proto_order (id: {}) not found at the beginning of the task'.format(context.proto_order_id))
        sys.exit()
    try:
        orders_api.create_or_update_order_from_proto_order(
            request=request,
            reserving=reserving,
            stocker=stocker,
            proto_order=context.proto_order,
            entrust_separate_seats=context.entrust_separate_seats,
            order_modifier=add_note,
            now=_now
        )
        transaction.commit()
        logging.info('order_import_task (%s) order_no (%s) ended with no errors' % (_proto_order.order_import_task.id, _proto_order.order_no))
    except OrderCreationError as e:
        transaction.abort()
        attributes = _proto_order.attributes
        if attributes is None:
            attributes = _proto_order.attributes = {}
        attributes.setdefault('errors', []).extend([unicode(e.message)])
        context._session.add(_proto_order)
        logging.info('order_import_task (%s) order_no (%s) ended with errors' % (_proto_order.order_import_task.id, _proto_order.order_no))
    finally:
        _proto_order.processed_at = _now
        context._session.commit()


@task_config(root_factory=ImportPerTaskResource,
             name="import_per_task",
             consumer="import_per_task",
             queue="import_per_task",
             timeout=1800,
             arguments={"maxPriority": 10})
def import_per_task(context, request):
    reserving = cart_api.get_reserving(request)
    stocker = cart_api.get_stocker(request)
    errors_dict = {}

    try:
        _task = context._session.query(orders_models.OrderImportTask).filter_by(id=context.order_import_task_id).one()
        logging.info('starting order_import_task (%s)...' % _task.id)
    except NoResultFound:
        logger.error('order_import_task (id: {}) not found at the beginning of the task'.format(context.order_import_task_id))
        sys.exit()

    try:
        orders_api.create_or_update_orders_from_proto_orders(
            request,
            reserving=reserving,
            stocker=stocker,
            proto_orders=context.order_import_task.proto_orders,
            import_type=context.order_import_task.import_type,
            allocation_mode=context.order_import_task.allocation_mode,
            entrust_separate_seats=context.order_import_task.entrust_separate_seats,
            enable_random_import=context.order_import_task.enable_random_import,
            order_modifier=add_note,
            channel_for_new_orders=ChannelEnum.IMPORT.v
        )
        transaction.commit()
        _task.status = orders_models.ImportStatusEnum.Imported.v
    except MassOrderCreationError as e:
        transaction.abort()
        errors_dict = dict(
            (ref, (errors_for_order[0].order_no, [error.message for error in errors_for_order]))
            for ref, errors_for_order in six.iteritems(e.errors)
        )
        _task.status = orders_models.ImportStatusEnum.Aborted.v
        logging.info('order_import_task (%s) ended with %s errors' % (_task.id, (unicode(len(errors_dict)) if errors_dict else u'no')))

    except Exception as e:
        logging.exception('order_import_task(%s) aborted: %s' % (_task.id, e))
        _task.status = orders_models.ImportStatusEnum.Aborted.v
    finally:
        if errors_dict:
            _task.errors = json.dumps(errors_dict)
            for ref, (order_no, errors_for_order) in six.iteritems(errors_dict):
                try:
                    proto_order = context._session.query(orders_models.ProtoOrder).filter_by(order_import_task=_task, ref=ref).one()
                    attributes = proto_order.attributes
                    if attributes is None:
                        attributes = proto_order.attributes = {}
                    attributes.setdefault('errors', []).extend(errors_for_order)
                    context._session.add(proto_order)
                except:
                    logger.exception(ref)
        else:
            _task.errors = None
        context._session.commit()