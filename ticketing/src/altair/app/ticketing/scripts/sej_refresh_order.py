# encoding: utf-8
import argparse
import logging
import sys
import csv
from datetime import datetime, timedelta

import sqlahelper
import transaction
from altair.app.ticketing.core.models import PointUseTypeEnum
from altair.app.ticketing.payments.api import lookup_plugin
from altair.app.ticketing.payments.plugins.sej import SejPluginFailure, determine_payment_type, build_sej_args, \
    get_tickets, \
    is_same_sej_order, refresh_skidata_barcode_if_necessary
from altair.app.ticketing.sej import api as sej_api
from altair.app.ticketing.sej import userside_api
from altair.app.ticketing.sej.exceptions import SejErrorBase
from altair.app.ticketing.sej.models import SejOrderUpdateReason
from altair.app.ticketing.sej.models import SejPaymentType
from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.sql.expression import desc

logger = logging.getLogger(__name__)


def message(msg, auxiliary=False):
    logger.log(auxiliary and logging.DEBUG or logging.INFO, msg)
    pad = '  ' if auxiliary else ''
    print >> sys.stderr, pad + msg


# order/apiのrefresh_order
def refresh_order(request, session, order, target_datetime):
    logger.info('Trying to refresh order %s (id=%d, payment_delivery_pair={ payment_method=%s, delivery_method=%s })...'
                % (order.order_no, order.id, order.payment_delivery_pair.payment_method.name,
                   order.payment_delivery_pair.delivery_method.name))
    payment_delivery_plugin, payment_plugin, delivery_plugin = lookup_plugin(request, order.payment_delivery_pair)

    regrant_number_due_at = datetime.strptime(target_datetime, '%Y-%m-%d %H:%M:%S')

    if payment_delivery_plugin is not None:
        logger.info('payment_delivery_plugin.refresh')
        payment_delivery_plugin_refresh(request, order, regrant_number_due_at=regrant_number_due_at)
    else:
        logger.info('payment_plugin.refresh')
        payment_delivery_plugin_refresh(request, order, regrant_number_due_at=regrant_number_due_at)
        logger.info('delivery_plugin.refresh')
        delivery_plugin_refresh(request, order, regrant_number_due_at=regrant_number_due_at)
    logger.info('Finished refreshing order %s (id=%d)' % (order.order_no, order.id))


# SejPaymentPluginのrefresh_order
def payment_delivery_plugin_refresh(request, order, current_date=None, regrant_number_due_at=None):
    if order.point_use_type == PointUseTypeEnum.AllUse:
        # 支払いのみで全額ポイント払いの場合はSejOrderがないので処理しない
        logger.info(u'skipped to refresh sej order due to full amount already paid by point')
        return
    if current_date is None:
        current_date = datetime.now()
    tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
    sej_refresh_order(
        request,
        tenant=tenant,
        order=order,
        update_reason=SejOrderUpdateReason.Change,
        current_date=current_date,
        regrant_number_due_at=regrant_number_due_at
    )


# SejDeliveryPluginのrefresh_order
def delivery_plugin_refresh(request, order, current_date=None, regrant_number_due_at=None):
    refresh_skidata_barcode_if_necessary(request, order)
    if current_date is None:
        current_date = datetime.now()
    tenant = userside_api.lookup_sej_tenant(request, order.organization_id)
    sej_refresh_order(
        request,
        tenant=tenant,
        order=order,
        update_reason=SejOrderUpdateReason.Change,
        current_date=current_date,
        regrant_number_due_at=regrant_number_due_at
    )


def sej_refresh_order(request, tenant, order, update_reason, current_date=None, regrant_number_due_at=None):
    from altair.app.ticketing.sej.models import _session
    if current_date is None:
        current_date = datetime.now()
    sej_order = sej_api.get_sej_order(order.order_no, session=_session)
    if sej_order is None:
        raise SejPluginFailure('no corresponding SejOrder found', order_no=order.order_no, back_url=None)

    # 代引もしくは前払後日発券の場合は payment_type の決定を再度行う (refs. #10350)
    if int(sej_order.payment_type) in (int(SejPaymentType.CashOnDelivery), int(SejPaymentType.Prepayment)):
        payment_type = int(determine_payment_type(current_date, order))
    else:
        payment_type = int(sej_order.payment_type)

    # ここのregrant_number_due_atが使われるため
    sej_args = build_sej_args(payment_type, order, order.created_at,
                              regrant_number_due_at=regrant_number_due_at)
    ticket_dicts = get_tickets(request, order)

    # 同一SejOrderを更新するためここを飛ばす
    #if is_same_sej_order(sej_order, sej_args, ticket_dicts):
    #    logger.info('the resulting order is the same as the old one; will do nothing')
    #    return

    if int(sej_order.payment_type) == SejPaymentType.PrepaymentOnly.v:
        if order.paid_at is not None:
            raise SejPluginFailure('already paid', order_no=order.order_no, back_url=None)
    else:
        if order.delivered_at is not None:
            raise SejPluginFailure('already delivered', order_no=order.order_no, back_url=None)

    if order.point_amount > 0 and sej_order.total_price > 0 >= order.payment_amount:
        # ポイント使用の予約の減額の場合、更新前の予約で支払が存在し、更新後で全額ポイント払いになる変更を許容しない
        # 一部ポイント払いから全額ポイント払いになり、支払方法が変わるような減額は許容しない。
        raise SejPluginFailure('failed to reduce the sej_order.total_price to 0',
                               order_no=order.order_no, back_url=None)

    if payment_type != int(sej_order.payment_type):
        logger.info('new sej order will be created as payment type is being changed: %d => %d' % (
            int(sej_order.payment_type), payment_type))

        new_sej_order = sej_order.new_branch(regrant_number_due_at=regrant_number_due_at)
        new_sej_order.tickets = sej_api.build_sej_tickets_from_dicts(
            sej_order.order_no,
            ticket_dicts,
            lambda idx: None
        )
        for k, v in sej_args.items():
            setattr(new_sej_order, k, v)
        new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

        try:
            new_sej_order = sej_api.do_sej_order(
                request,
                tenant=tenant,
                sej_order=new_sej_order,
                session=_session
            )
            sej_api.cancel_sej_order(request, tenant=tenant, sej_order=sej_order, origin_order=order, now=current_date)
        except SejErrorBase:
            raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)
    else:
        new_sej_order = sej_order.new_branch(regrant_number_due_at=regrant_number_due_at)
        new_sej_order.tickets = sej_api.build_sej_tickets_from_dicts(
            sej_order.order_no,
            ticket_dicts,
            lambda idx: None
        )
        for k, v in sej_args.items():
            setattr(new_sej_order, k, v)
        new_sej_order.total_ticket_count = new_sej_order.ticket_count = len(new_sej_order.tickets)

        try:
            new_sej_order = sej_api.refresh_sej_order(
                request,
                tenant=tenant,
                sej_order=new_sej_order,
                update_reason=update_reason,
                session=_session
            )
            sej_order.cancel_at = new_sej_order.created_at
            _session.add(sej_order)
            _session.commit()
        except SejErrorBase:
            raise SejPluginFailure('refresh_order', order_no=order.order_no, back_url=None)


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config_uri', metavar='config', type=str,
                        help='config file')
    parser.add_argument('--max_regrant_number_due_at', action='store_true')
    parser.add_argument('target_datetime', metavar='target_datetime', type=str,
                        help='target_datetime')
    parser.add_argument('order_no', metavar='order_no', type=str, nargs='*',
                        help='order_no')
    parser.add_argument('--order_no_in_file', metavar='load order_no in file', type=argparse.FileType('r'))
    args = parser.parse_args()

    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)
    request = env['request']

    session = sqlahelper.get_session()
    target_datetime = args.target_datetime
    max_regrant_number_due_at = args.max_regrant_number_due_at

    from altair.app.ticketing.orders.models import Order

    def match_order_no(_order_no):
        _order = session.query(Order).filter_by(order_no=_order_no).order_by(desc(Order.branch_no)).first()
        if _order is None:
            raise Exception('Order %s could not be found' % _order_no)
        if _order.canceled_at is not None:
            raise Exception('order %s has already been calceled' % _order_no)
        orders.append(_order_no)

    try:
        orders = []
        order_no_list = []
        for order_no in args.order_no:
            match_order_no(order_no)
        if args.order_no_in_file is not None:
            with open(args.order_no_in_file.name) as f:
                reader = csv.reader(f)
                for order_no in reader:
                    order_no_list.append(order_no[0])
            for order_no in order_no_list:
                match_order_no(order_no)
        for order_no in orders:
            order = session.query(Order).filter_by(order_no=order_no).order_by(desc(Order.branch_no)).first()
            try:
                target_regrant_number_due_at = target_datetime
                if max_regrant_number_due_at:
                    target_regrant_number_due_at = (order.created_at + timedelta(days=364)).strftime(
                        '%Y-%m-%d %H:%M:%S')
                refresh_order(request, session, order, target_regrant_number_due_at)
            except Exception as e:
                message('failed to refresh order %s: %s' % (order_no, e))
                logger.exception(u'failed to refresh order %s' % order_no)
            finally:
                transaction.commit()

    except Exception as e:
        raise
        message(e.message)


if __name__ == '__main__':
    main()
