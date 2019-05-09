#! /usr/bin/env python
# coding=utf-8

from __future__ import unicode_literals

import argparse
import codecs
import csv
import logging
import os
import sys
from argparse import ArgumentParser
from collections import OrderedDict

from sqlalchemy.sql.expression import and_

from altair.app.ticketing.orders.models import Order
from altair.sqlahelper import get_db_session
from pyramid.paster import bootstrap, setup_logging

from altair.app.ticketing.core.models import Performance, ShippingAddress
from altair.app.ticketing.lots.models import Lot, LotEntry, LotEntryWish, LotElectWork, LotRejectWork
from altair.app.ticketing.users.models import UserCredential, Membership

logger = logging.getLogger(__name__)


class EncodingCheckAction(argparse.Action):
    """Action class to validate the given encoding"""
    def __call__(self, parser, namespace, values, option_string=None):
        if values:
            try:
                codecs.lookup(values)
            except LookupError:
                print('unknown encoding name: {}'.format(values))
                sys.exit(1)
        setattr(namespace, self.dest, values)


def get_lot_entry_status(sql_res):
    if sql_res.lot_entry_wish_withdrawn_at:
        status = 'ユーザー取消'
    elif sql_res.lot_entry_wish_elected_at:
        status = '当選'
    elif sql_res.lot_entry_wish_rejected_at:
        status = '落選'
    elif sql_res.lot_entry_canceled_at:
        status = 'キャンセル'
    elif sql_res.lot_elect_work_entry_no:
        status = '当選予定'
    elif sql_res.lot_reject_work_entry_no:
        status = '落選予定'
    elif sql_res.lot_entry_closed_at:
        status = '終了'
    else:
        status = '申込'
    return status


def get_paid_status(sql_res):
    # return empty if lot entry is not elected status
    if not sql_res.lot_entry_wish_elected_at:
        return ''
    return '入金済み' if sql_res.order_paid_at else '未入金'


FUNC = {  # dict whose value's function is called when the corresponding key name is extracted
    'lot_entry_status': get_lot_entry_status,
    'order_paid_at': get_paid_status,
    'lot_entry_wish_wish_order': lambda s: s.lot_entry_wish_wish_order + 1,
}

COLUMN = OrderedDict([
    ('user_credential_authz_identifier', '会員番号'),
    ('lot_entry_wish_wish_order', '希望順序'),
    ('shipping_address_email', '申込者メールアドレス'),
    ('lot_entry_status', '当落ステータス'),
    ('order_paid_at', '入金ステータス'),
    ('performance_start_on', '公演日時'),
    ('shipping_address_prefecture', '申込者都道府県'),
    ('lot_entry_no', '申込番号'),
])


def get_query(session, lot_id):
    """Select columns of data CAM wants (ref. tkt-7447)"""
    return session.query(
        LotEntry.entry_no.label('lot_entry_no'),
        LotEntry.canceled_at.label('lot_entry_canceled_at'),
        LotEntry.closed_at.label('lot_entry_closed_at'),
        LotEntryWish.withdrawn_at.label('lot_entry_wish_withdrawn_at'),
        LotEntryWish.elected_at.label('lot_entry_wish_elected_at'),
        LotEntryWish.rejected_at.label('lot_entry_wish_rejected_at'),
        LotEntryWish.wish_order.label('lot_entry_wish_wish_order'),
        LotElectWork.lot_entry_no.label('lot_elect_work_entry_no'),
        LotRejectWork.lot_entry_no.label('lot_reject_work_entry_no'),
        Order.paid_at.label('order_paid_at'),
        ShippingAddress.email_1.label('shipping_address_email'),
        ShippingAddress.prefecture.label('shipping_address_prefecture'),
        Performance.start_on.label('performance_start_on'),
        UserCredential.authz_identifier.label('user_credential_authz_identifier'))\
        .join(Lot, Lot.id == LotEntry.lot_id) \
        .join(LotEntryWish, LotEntryWish.lot_entry_id == LotEntry.id) \
        .join(ShippingAddress, ShippingAddress.id == LotEntry.shipping_address_id) \
        .join(Performance, Performance.id == LotEntryWish.performance_id)\
        .outerjoin(LotElectWork, and_(LotElectWork.lot_entry_no == LotEntry.entry_no,
                                      LotElectWork.lot_id == LotEntry.lot_id,
                                      LotElectWork.wish_order == LotEntryWish.wish_order))\
        .outerjoin(LotRejectWork, and_(LotRejectWork.lot_entry_no == LotEntry.entry_no,
                                       LotRejectWork.lot_id == LotEntry.lot_id))\
        .outerjoin(Membership, Membership.id == LotEntry.membership_id)\
        .outerjoin(UserCredential, UserCredential.user_id == LotEntry.user_id) \
        .outerjoin(Order, Order.id == LotEntry.order_id) \
        .filter(LotEntry.lot_id == lot_id)\
        .all()


def build_csv_row(sql_res, encoding):
    """Create a list used to be written as a csv row"""
    row = []
    for k in COLUMN.keys():
        # get the value from SQL result
        # function is called in stead if it's included in FUNC dict
        ret_val = FUNC[k](sql_res) if k in FUNC else getattr(sql_res, k)

        if type(ret_val) is unicode:
            ret_val = ret_val.encode(encoding)
        row.append(ret_val)
    return row


def write_csv(request, lot_id, output_path, encoding):
    """Write extracted data as csv format"""
    session = get_db_session(request, name='slave')
    try:
        results = get_query(session, lot_id)
        if len(results) == 0:
            logger.info('no lot entry linking to lot id = {}'.format(lot_id))

        # append filename if the given output path is dir
        if os.path.isdir(output_path):
            output_path = os.path.join(output_path, 'lot-{}.csv'.format(lot_id))

        with open(output_path, 'w') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=','.encode(encoding),
                                    quotechar='"'.encode(encoding), quoting=csv.QUOTE_MINIMAL)
            spamwriter.writerow([v.encode(encoding) for v in COLUMN.values()])

            for result in results:
                spamwriter.writerow(build_csv_row(result, encoding))
        csvfile.close()

    except Exception as e:
        logger.error('Failed to export LotEntry data.')
        raise e


def main():
    """抽選申込の情報を申込希望単位でCSVファイルに出力します。
    このスクリプトは抽出されるデータをCAMに渡すために作られたので、抽出項目はCAMが要求するものだけに絞ります。(ref. tkt-7447)
    """
    # load arguments
    parser = ArgumentParser(description='Export LotEntry data on their wishes basis.')
    parser.add_argument('--config', type=str, required=True, help='config file')
    parser.add_argument('--lot_id', type=int, required=True)
    parser.add_argument('--output', type=str, required=True, help='path of either output file or dir')
    parser.add_argument('--encoding', type=str, required=False, default='utf-8',
                        action=EncodingCheckAction, help='encoding name of output file ')

    args = parser.parse_args()
    config = args.config
    setup_logging(config)

    env = bootstrap(config)
    request = env['request']

    # export lot entry data linking to the given lot id to csv file
    write_csv(request, args.lot_id, args.output, args.encoding)
