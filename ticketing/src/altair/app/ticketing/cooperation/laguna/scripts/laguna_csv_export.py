#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""laguna用csvの出力
"""
import six
import os
import sys
import csv
import time
import shutil
import zipfile
import logging
import argparse
import datetime
import itertools

import scp
import enum
import paramiko
import pyminizip
import sqlalchemy.orm as sa_orm
import sqlalchemy.sql.expression as sa_exp

import pyramid.threadlocal
from pyramid.paster import (
    bootstrap,
    setup_logging,
    )
from pyramid.renderers import render_to_response

if six.PY3:
    from os import makedirs
else:
    def makedirs(path, mode=0o777, exist_ok=False):
        if os.path.exists(path):
            return
        return os.makedirs(path, mode)

from altair import multilock
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import (
    ShippingAddress,
    Event,
    Performance,
    SalesSegment,
    SalesSegmentGroup,
    PaymentMethod,
    DeliveryMethod,
    Venue,
    PaymentDeliveryMethodPair,
    Mailer,
    )
from altair.app.ticketing.users.models import (
    User,
    UserProfile,
    UserCredential,
    Member,
    MemberGroup,
    Membership,
    )
from altair.app.ticketing.orders.models import Order
from altair.app.ticketing.lots.models import (
    Lot,
    LotEntry,
    )
from altair.app.ticketing.orders.dump import OrderExporter

logger = logging.getLogger(__name__)
LAGUNA_ORG_ID = 43


MAIL_MAG_FIELD_NAME = 'メールマガジン受信可否'
CHANNEL_FIELD_NAME = '販売チャネル'

format_datetime = lambda dt: dt and dt.strftime('%Y-%m-%d %H:%M:%S')  # 日付のフォーマット用


class MailMagStatus(enum.Enum):
    """メールマガジン受信可否のステータス
    """
    ALLOW = 1  # 許可
    DENY = ''  # 拒否


# synagy専用のcsvヘッダ
synagy_header_lots = [
    '状態',
    '申し込み番号',
    '希望順序',
    '申し込み日',
    '席種',
    '枚数',
    'イベント',
    '会場',
    '公演',
    '公演日',
    '決済方法',
    '引取方法',
    '配送先姓',
    '配送先名',
    '配送先姓(カナ)',
    '配送先名(カナ)',
    '郵便番号',
    '国',
    '都道府県',
    '市区町村',
    '住所1',
    '住所2',
    '電話番号1',
    '電話番号2',
    'メールアドレス1',
    'メールアドレス2',
    '性別',
    '誕生日',
    CHANNEL_FIELD_NAME,
    ]

synagy_header_orders = [
    '予約番号',
    'ステータス',
    '決済ステータス',
    '予約日時',
    '支払日時',
    '合計金額',
    '決済手数料',
    '配送手数料',
    'システム利用料',
    '特別手数料',
    '内手数料金額',
    '払戻合計金額',
    '払戻決済手数料',
    '払戻配送手数料',
    '払戻システム利用料',
    '払戻特別手数料',
    '発券開始日時',
    '発券期限',
    '支払開始日時',
    '支払期限',
    MAIL_MAG_FIELD_NAME,
    '性別',
    '会員種別名',
    '会員グループ名',
    '会員種別ID',
    '配送先姓',
    '配送先名',
    '配送先姓(カナ)',
    '配送先名(カナ)',
    '郵便番号',
    '国',
    '都道府県',
    '市区町村',
    '住所1',
    '住所2',
    '電話番号1',
    '電話番号2',
    'メールアドレス1',
    'メールアドレス2',
    '決済方法',
    '引取方法',
    'イベント',
    '公演',
    '公演日',
    '会場',
    '席種',
    '商品個数',
    ]

synagy_header_attributes = [
    'attribute[項目1]',
    'attribute[項目2]',
    'attribute[項目3]',
    'attribute[項目4]',
    'attribute[項目5]',
    ]

synagy_header = synagy_header_lots + synagy_header_orders + synagy_header_attributes

MAIL_MAG_FIELD_INDEX = synagy_header.index(MAIL_MAG_FIELD_NAME)
CHANNEL_FIELD_INDEX = synagy_header.index(CHANNEL_FIELD_NAME)
ATTRIBUTE_COL_COUNT = len(synagy_header_attributes)


def export_csv_for_laguna(request, fileobj, organization_id):
    writer = csv.writer(fileobj)

    session = get_db_session(request, name='slave')
    now = datetime.datetime.now()
    start = datetime.datetime(now.year, 1, 1, 0, 0)
    end = datetime.datetime(now.year, 12, 31, 23, 59)

    orders = Order \
        .query \
        .join(ShippingAddress) \
        .join(PaymentDeliveryMethodPair) \
        .join(Performance) \
        .join(Venue, Venue.performance_id == Performance.id) \
        .join(Event, Event.id == Performance.event_id) \
        .join(SalesSegment, SalesSegment.performance_id == Performance.id) \
        .join(SalesSegmentGroup) \
        .outerjoin(User, Order.user) \
        .outerjoin(UserProfile) \
        .outerjoin(UserCredential) \
        .outerjoin(Member) \
        .outerjoin(MemberGroup) \
        .outerjoin(Membership) \
        .filter(Order.organization_id == organization_id) \
        .filter(Order.created_at.between(start, end))

    entries = LotEntry \
        .query \
        .join(Lot) \
        .join(Event) \
        .join(PaymentDeliveryMethodPair) \
        .join(PaymentMethod) \
        .join(DeliveryMethod) \
        .join(ShippingAddress) \
        .filter(LotEntry.organization_id == organization_id)\
        .filter(LotEntry.created_at.between(start, end)) \
        .filter(sa_exp.or_(
            LotEntry.elected_at != None,
            LotEntry.rejected_at != None,
            )) \
        .options(sa_orm.joinedload('shipping_address')) \
        .options(sa_orm.joinedload('wishes')) \
        .options(sa_orm.joinedload('wishes.products'))

    # order_nos = [order.order_no for order in orders]
    order_no_order = [(order.order_no, [order, None]) for order in orders]
    entry_no_entry = [(entry.entry_no, [None, entry]) for entry in entries]

    mails = itertools.chain(
        itertools.chain.from_iterable([(order.shipping_address.email_1, order.shipping_address.email_2) for order in orders]),
        itertools.chain.from_iterable([(entry.shipping_address.email_1, entry.shipping_address.email_2) for entry in entries]),
        )
    order_exporter = OrderExporter(session, organization_id)
    subscribed_emails = set(mail[0] for mail in order_exporter.get_subscribed_emails(organization_id, mails))
    get_order_no = lambda record: record[0]
    order_no_record = sorted(order_no_order + entry_no_entry, key=get_order_no)
    writer.writerow(synagy_header)  # header書き込み
    error_records = []

    for order_no, number_order_entry_pair in itertools.groupby(order_no_record, key=get_order_no):
        order = None
        entry = None
        channel = ''
        rec = []
        attribute_values = []
        current_mails = []  # この申込/予約に関係するメールアドレスのリスト
        for number, order_entry in number_order_entry_pair:
            tmp_order, tmp_entry = order_entry
            if tmp_order:
                order = tmp_order
            elif tmp_entry:
                entry = tmp_entry

        if entry:
            channel = entry.channel
            wish_order = 0
            for _wish in entry.wishes:
                if _wish.elected_at:
                    wish_order = _wish.wish_order
                    break
            wish = entry.get_wish(wish_order)
            quantity = sum(product.quantity for product in wish.products)
            products = list(set(lot_entry_product.product for lot_entry_product in wish.products))
            if not products:  # LotEntryProduct.deleted_atを立てた場合はそのデータは送らない
                continue
            stock_type_name = products[0].seat_stock_type.name if products else ''

            if entry.attributes:
                # 1番目2番目は先着側では性別/誕生日として使っている
                # それをskipする形で出力させたいため
                # 抽選申込は1番目の項目をcsv上では3番目から出力する
                attribute_values = itertools.chain(
                    [entry.birthday, entry.gender],
                    (value for name, value in sorted(entry.attributes.items())),
                    )

            current_mails += [
                entry.shipping_address.email_1,
                entry.shipping_address.email_2,
                ]

            rec += [
                wish.status,
                entry.entry_no,
                wish.wish_order + 1,  # 0が第一希望
                format_datetime(entry.created_at),
                stock_type_name,
                quantity,
                entry.lot.event.title,
                wish.performance.venue.name,
                wish.performance.name,
                wish.performance.start_on,
                entry.payment_delivery_pair.payment_method.name,
                entry.payment_delivery_pair.delivery_method.name,
                entry.shipping_address.last_name,
                entry.shipping_address.first_name,
                entry.shipping_address.last_name_kana,
                entry.shipping_address.first_name_kana,
                entry.shipping_address.zip,
                entry.shipping_address.country,
                entry.shipping_address.prefecture,
                entry.shipping_address.city,
                entry.shipping_address.address_1,
                entry.shipping_address.address_2,
                entry.shipping_address.tel_1,
                entry.shipping_address.tel_2,
                entry.shipping_address.email_1,
                entry.shipping_address.email_2,
                entry.gender,
                entry.birthday,
                entry.channel,
                ]
        else:
            rec += ['' for ii in range(len(synagy_header_lots))]

        if order:
            if order.is_inner_channel:  # inner channelの予約は必要なデータが揃っていないケースが考えられるので送信しない
                continue

            if order.channel:
                channel = order.channel
            sex = order.user.user_profile.sex if order.user and order.user.user_profile else ''
            auth_identifier = order.user.first_user_credential.auth_identifier if order.user and order.user.user_credential else ''
            member = order.user.member if order.user else None
            quantity = sum(ordered_product.quantity for ordered_product in order.ordered_products)
            products = list(set(ordered_product.product for ordered_product in order.ordered_products))
            # assert len(products) == 1, '商品は一つでなければならない'
            # product = products[0]
            product = products[0]
            stock_type = product.seat_stock_type
            margin_ratio = order.sales_segment.margin_ratio
            margin = sum(
                ordered_product.price * ordered_product.quantity * (margin_ratio / 100)
                for ordered_product in order.ordered_products
                )

            if order.attributes:
                name_value = dict(order.attributes)
                attribute_values.append(name_value.pop(u'生年月日'))
                attribute_values.append(name_value.pop(u'性別'))
                values = [value for name, value in sorted(name_value.items())][:3]
                attribute_values += values

            current_mails += [
                order.shipping_address.email_1,
                order.shipping_address.email_2,
                ]

            rec += [
                order.order_no,
                order.status,
                order.payment_status,
                format_datetime(order.created_at),
                format_datetime(order.paid_at),
                order.total_amount,
                order.transaction_fee,
                order.delivery_fee,
                order.system_fee,
                order.special_fee,
                margin,
                order.refund_total_amount,
                order.refund_transaction_fee,
                order.refund_delivery_fee,
                order.refund_system_fee,
                order.refund_special_fee,
                format_datetime(order.issuing_start_at),
                format_datetime(order.issuing_end_at),
                format_datetime(order.payment_start_at),
                format_datetime(order.payment_due_at),
                MailMagStatus.DENY.value,  # メール受信可否 ここのフィールドは後で上書きする
                sex,
                member.member_group.member_ship.name if member else '',
                member.member_group.name if member else '',
                auth_identifier,
                order.shipping_address.last_name,
                order.shipping_address.first_name,
                order.shipping_address.last_name_kana,
                order.shipping_address.first_name_kana,
                order.shipping_address.zip,
                order.shipping_address.country,
                order.shipping_address.prefecture,
                order.shipping_address.city,
                order.shipping_address.address_1,
                order.shipping_address.address_2,
                order.shipping_address.tel_1,
                order.shipping_address.tel_2,
                order.shipping_address.email_1,
                order.shipping_address.email_2,
                order.payment_delivery_pair.payment_method.name,
                order.payment_delivery_pair.delivery_method.name,
                order.performance.event.title,
                order.performance.name,
                format_datetime(order.performance.start_on),
                order.performance.venue.name,
                stock_type.name,
                quantity,
                ]
        else:
            rec += ['' for ii in range(len(synagy_header_orders))]

        for current_mail in set(current_mails):  # メール受信可否設定を上書き
            if current_mail in subscribed_emails:
                rec[MAIL_MAG_FIELD_INDEX] = MailMagStatus.ALLOW.value  # メール受信可否のフィールドを上書き
                break
        rec[CHANNEL_FIELD_INDEX] = '' if channel is None else channel  # チャネルを設定

        # order and lot entry attributes
        # 存在する方を出力(両方あったらOrderAttributeを出力)
        attribute_values = list(attribute_values)
        rec_attriubtes = ['' for ii in range(ATTRIBUTE_COL_COUNT)]
        for ii, value in enumerate(attribute_values[:ATTRIBUTE_COL_COUNT]):
            rec_attriubtes[ii] = value

        rec += rec_attriubtes
        rec = map(safe_encoding, rec)

        if verify_record(rec):
            writer.writerow(rec)
        else:
            error_records.append(rec)
    return error_records


# 抽選
LOT_COLUMN_START_INDEX = 0
LOT_COLUMN_END_INDEX = 28
LOT_COLUMN_INDEXES = range(LOT_COLUMN_START_INDEX, LOT_COLUMN_END_INDEX+1)
LOT_UNNEED_COLUMN_INDEXES = (  # 空文字が許容されるcolumn
    21,  # 住所2
    )
LOT_OR_COLUMN_INDEX_PAIRS = (  # どちらかが入っていれば良いcolumn
    (22, 23),  # 電話番号
    (24, 25),  # メールアドレス
    )


# 先着
ORDER_COLUMN_START_INDEX = 29
ORDER_COLUMN_END_INDEX = 75
ORDER_COLUMN_INDEXES = range(ORDER_COLUMN_START_INDEX, ORDER_COLUMN_END_INDEX+1)
ORDER_UNNEED_COLUMN_INDEXES = (  # 空文字が許容されるcolumn
    49,  # メールマガジン(これは抽選/先着共通だけど拒否の場合はブランクになる)
    50,  # 性別
    51,  # 会員種別
    52,  # 会員グループ名
    53,  # 会員種別ID
    63,  # 住所2
    )
ORDER_OR_COLUMN_INDEX_PAIRS = (  # どちらかが入っていれば良いcolumn
    (64, 65),  # 電話番号
    (66, 67),  # メールアドレス
    )
ORDER_UNNEED_COLUMN_INDEXES_ALL = ORDER_UNNEED_COLUMN_INDEXES

# 追加情報
ATTRIBUTE_COLUMN_START_INDEX = 76
ATTRIBUTE_COLUMN_END_INDEX = 80
ATTRIBUTE_COLUMN_INDEXES = range(ATTRIBUTE_COLUMN_START_INDEX, ATTRIBUTE_COLUMN_END_INDEX+1)


def verify_record(rec):
    """レコードがラグーナカスタム側が想定しているデータかどうかを検証
    """
    if rec[LOT_COLUMN_START_INDEX]:  # 抽選
        unneed_indexes = list(itertools.chain(LOT_UNNEED_COLUMN_INDEXES, *LOT_OR_COLUMN_INDEX_PAIRS))
        for ii, data in enumerate(rec):
            if ii not in unneed_indexes and not data:
                return False
        for indexes in LOT_OR_COLUMN_INDEX_PAIRS:
            if not any(rec[idx] for idx in indexes):
                return False
    elif rec[ORDER_COLUMN_START_INDEX]:  # 先着 もしくは 当選処理後抽選
        unneed_indexes = list(itertools.chain(ORDER_UNNEED_COLUMN_INDEXES, *ORDER_OR_COLUMN_INDEX_PAIRS))
        for ii, data in enumerate(rec):
            if ii not in unneed_indexes and not data:
                return False
        for indexes in ORDER_OR_COLUMN_INDEX_PAIRS:
            if not any(rec[idx] for idx in indexes):
                return False

    # 共通
    try:
        datetime.datetime.strftime('%Y-%m-%d', rec[76])  # 生年月日
        int(rec[77])  # 性別
        int(rec[78])  # 質問項目１
        int(rec[79])  # 質問項目２
        int(rec[80])  # 質問項目３
    except (IndexError, TypeError, ValueError) as err:
        logger.warn(err)
        return False
    return True


def send_error_mail(error_records, mailer, recipients, sender):
    subject = 'ラグーナカスタムデータ連携エラー'
    template_path = 'altair.app.ticketing:templates/cooperation/laguna/mails/error_mail.txt',
    body = render_to_response(template_path, error_records)
    mailer.create_message(
        sender=sender,
        recipient=recipients,
        subject=subject,
        body=body.text,
        )
    mailer.send(sender, [recipients])


def safe_encoding(x):
    return x.encode('utf8') if hasattr(x, 'encode') else x


def compress(fp, password):
    stamp = time.strftime('%Y%m%d')
    csv_name = '{}.csv'.format(stamp)
    zip_name = '{}.zip'.format(stamp)

    zfile = zipfile.ZipFile(zip_name, mode='w')
    fp.seek(0)
    zfile.writestr(csv_name, fp.read())
    zfile.close()
    return zip_name


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('--no-send', dest='no_send', default=False, action='store_true')
    parser.add_argument('--organization_id', default=LAGUNA_ORG_ID, type=int)
    args = parser.parse_args()

    if not args.stdout:
        setup_logging(args.conf)
    env = bootstrap(args.conf)
    settings = env['registry'].settings
    request = pyramid.threadlocal.get_current_request()

    var_dir = settings['laguna.var_dir']
    host = settings['laguna.host']
    port = int(settings['laguna.port'])
    user = settings['laguna.user']
    dir_ = settings['laguna.dir']
    private_key = settings['laguna.private_key']
    zip_password = settings['laguna.zip_password']
    staging = os.path.join(var_dir, 'staging')
    pending = os.path.join(var_dir, 'pending')
    makedirs(staging, exist_ok=True)
    makedirs(pending, exist_ok=True)

    recipients = map(lambda s: s.strip(), settings['laguna.mail.recipient'].split(','))
    sender = settings['laguna.mail.sender']

    try:
        with multilock.MultiStartLock('laguna_csv'):
            error_records = []
            stamp = time.strftime('%Y%m%d')
            csv_path = os.path.join(staging, 'TS{}.CSV'.format(stamp))
            zip_filename = 'TS{}.zip'.format(stamp)
            zip_path = os.path.join(staging, zip_filename)
            with open(csv_path, 'w+b') as fp:
                error_records = export_csv_for_laguna(request, fp, args.organization_id)
            pyminizip.compress(csv_path, zip_path, zip_password, 9)
            os.remove(csv_path)
            rc = 0
            if not args.no_send:
                client = paramiko.SSHClient()
                policy = paramiko.AutoAddPolicy()
                client.set_missing_host_key_policy(policy)
                client.connect(host, port, user, key_filename=private_key)
                scp_client = scp.SCPClient(client.get_transport())
                dst = os.path.join(dir_, zip_filename)
                scp_client.put(zip_path, dst)
                timestamp = time.strftime('%Y%m%d%H%M%S')
                pending_filepath = os.path.join(pending, '{}.{}'.format(zip_filename, timestamp))
                shutil.move(zip_path, pending_filepath)

            if error_records:
                mailer = Mailer(settings)
                send_error_mail(error_records, mailer, recipients, sender)

            return rc
    except multilock.AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))

if __name__ == '__main__':
    main()
