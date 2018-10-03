# -*- coding: utf-8 -*-

import json
import logging
import re
import six
import sys
import transaction
from datetime import datetime
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound

from altair.mq.decorators import task_config

from altair.app.ticketing.cart import api as cart_api
from altair.app.ticketing.core.models import ChannelEnum, TicketBundle
from altair.app.ticketing.payments import plugins as payments_plugins
from altair.app.ticketing.orders import api as orders_api
from altair.app.ticketing.orders import models as orders_models
from altair.app.ticketing.orders.exceptions import OrderCreationError, MassOrderCreationError

from .resources import (ImportPerOrderResource, ImportPerTaskResource, RefreshOrderResource)

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
             timeout=3600,
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
        _task.errors = None
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
        _task.errors = json.dumps({u'予想外エラー': (u'-', [str(e)])})

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
                except Exception:
                    logger.exception(ref)

        context._session.commit()


@task_config(root_factory=RefreshOrderResource,
             name="notify_update_ticket_info",
             consumer="notify_update_ticket_info",
             queue="notify_update_ticket_info",
             timeout=3600,
             arguments={"maxPriority": 10})
def notify_update_ticket_info(context, request):
    """現行の券面構成をSEJとFMに通知するため、orders.apiのrefresh_orderを利用して予約を更新する"""
    from altair.app.ticketing.events.tickets.models import NotifyUpdateTicketInfoTask
    from altair.app.ticketing.orders.models import NotifyUpdateTicketInfoTaskEnum

    bundle_id = request.POST.get('bundle_id')
    if bundle_id is None:
        raise ValueError('bundle_id must be given by POST method.')

    try:
        # チケット券面構成情報とタスクを取得
        bundle = TicketBundle.query.filter_by(id=bundle_id).one()
        task = NotifyUpdateTicketInfoTask.filter_by(
            ticket_bundle_id=bundle_id
        ).order_by(
            NotifyUpdateTicketInfoTask.id.desc()
        ).first()

        if task is None:
            raise ValueError('the task record was not found.')

    except (MultipleResultsFound, NoResultFound, ValueError) as err:
        raise ValueError('required infomation for this task is missing: {}'.format(err.message))

    # タスクステータス更新
    transaction.begin()
    task.status = NotifyUpdateTicketInfoTaskEnum.progressing.v[0]
    task.save()
    transaction.commit()

    now = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    errors = []
    logger.info('SEJ/FM orders linked to bundle_id:{} will be refreshed.'.format(bundle_id))

    # 券面に紐づく未発券予約を取得し、1件ずつ更新通知
    for o in bundle.not_issued_sej_fm_orders():
        try:
            # メモ欄に履歴を追記
            o.note = u'\n'.join([
                o.note if o.note is not None else u'',
                u'「更新をSEJ / FMに通知」ボタンによる予約更新実行: {}'.format(now)
            ])

            # 予約更新実施
            orders_api.refresh_order(request, context._session, o)

        except Exception as err:
            errors.append(u'order_no:{}の更新通知に失敗。システムエラー内容: {}'.format(o.order_no, err.message))

    if errors:
        task.status = NotifyUpdateTicketInfoTaskEnum.failed.v[0]
        task.errors = u'\n'.join(errors)
        logger.error(u'failed to refresh {} order(s): {}'.format(len(errors), task.errors))
    else:
        task.status = NotifyUpdateTicketInfoTaskEnum.completed.v[0]
        logger.info('SEJ/FM orders linked to bundle_id:{} were successfully refreshed.'.format(bundle_id))

    # タスク情報更新
    task.save()
