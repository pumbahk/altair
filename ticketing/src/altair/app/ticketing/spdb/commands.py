# -*- coding:utf-8 -*-
import os
import sys
import uuid
import logging
import socket
import gzip
import shutil
from pymysql import connect, cursors
from pyramid.paster import bootstrap, setup_logging
import argparse
from datetime import datetime, timedelta
from paramiko import SSHClient, AutoAddPolicy

logger = logging.getLogger(__name__)


spdb_sql = """
    SELECT
        CONCAT(`Order`.order_no, OrderedProductItemToken.serial) as PrimaryKey,
        `Order`.order_no,
        CASE
            WHEN `Order`.canceled_at IS NOT NULL THEN 'canceled'
            WHEN delivered_at IS NOT NULL THEN 'delivered'
            ELSE 'ordered'
        END AS order_status,
        CASE
            WHEN `Order`.refund_id IS NOT NULL AND `Order`.refunded_at IS NULL THEN 'refunding'
            WHEN refunded_at IS NOT NULL THEN 'refunded'
            WHEN paid_at IS NOT NULL THEN 'paid'
            ELSE 'unpaid'
        END AS payment_status,
        `Order`.created_at,
        `Order`.user_id,
        Event.id as event_id,
        Event.title as event_title,
        Performance.id as performance_id,
        Performance.name as performance_name,
        Performance.start_on as performance_start_on,
        ProductItem.name as product_item_name,
        Seat.name as seat_name,
        ProductItem.price as product_item_price,
        ProductItem.quantity as product_item_quantity,
        `Order`.system_fee + `Order`.special_fee + `Order`.delivery_fee + `Order`.transaction_fee AS fee,
        `Order`.total_amount,
        UserCredential.authz_identifier,
        Membership.name as membership_name,
        MemberGroup.name as membergroup_name,
        PointGrantHistoryEntry.amount as point,
        CASE PaymentMethod.payment_plugin_id WHEN 1 THEN 'マルチ決済' WHEN 2 THEN 'ID決済' WHEN 3 THEN 'セブン' WHEN 4 THEN '窓口' WHEN 5 THEN '無料' WHEN 6 THEN 'ファミマ' ELSE '不明' END AS payment_method,
        CASE DeliveryMethod.delivery_plugin_id WHEN 1 THEN '配送' WHEN 2 THEN 'セブン' WHEN 3 THEN '窓口' WHEN 4 THEN 'QR認証' WHEN 5 THEN 'イベントゲート' WHEN 6 THEN' ファミマ' ELSE '不明' END AS delivery_method,
        Cart.user_agent

    FROM
        `Order`
    JOIN Cart ON Cart.order_id = `Order`.id
    JOIN Performance ON `Order`.performance_id = Performance.id
    JOIN Event ON Event.id = Performance.event_id
    JOIN OrderedProduct ON OrderedProduct.order_id = `Order`.id
    JOIN OrderedProductItem ON OrderedProductItem.ordered_product_id = OrderedProduct.id
    JOIN OrderedProductItemToken ON OrderedProductItemToken.ordered_product_item_id = OrderedProductItem.id
    JOIN Product ON OrderedProduct.product_id = Product.id
    JOIN ProductItem ON OrderedProductItem.product_item_id = ProductItem.id
    LEFT JOIN Seat ON Seat.id = OrderedProductItemToken.seat_id
    LEFT JOIN UserCredential ON UserCredential.user_id = `Order`.user_id
    LEFT JOIN MemberGroup ON MemberGroup.id = `Order`.membergroup_id
    LEFT JOIN Membership ON Membership.id = MemberGroup.membership_id
    LEFT JOIN PointGrantHistoryEntry ON PointGrantHistoryEntry.order_id = `Order`.id
    JOIN PaymentDeliveryMethodPair ON PaymentDeliveryMethodPair.id = `Order`.payment_delivery_method_pair_id
    JOIN PaymentMethod ON PaymentMethod.id = PaymentDeliveryMethodPair.payment_method_id
    JOIN DeliveryMethod ON DeliveryMethod.id = PaymentDeliveryMethodPair.delivery_method_id
"""


class SQLCreater(object):
    def __init__(self, args, sql):
        self._args = args
        self._sql = sql

    @property
    def sql(self):
        if self._args.org:
            sql = "{0} WHERE `Order`.organization_id = {1}".format(self._sql, self._args.org)

        """
        期間指定
        何も指定されなかったら、昨日1日分を取得する。
        fromだけ指定されたら、その日1日分を取得する。
        toが指定されたら、toで指定された日、1日分も取得する。
        ex) -f 2016/12/1 -t 2016/12/5の場合、2016/12/1 00:00:00 - 2016/12/6 00:00:00
        toだけ指定されたら、fromは昨日の00:00:00〜とする。
        """
        term_to = datetime.strptime(datetime.now().date().strftime('%Y/%m/%d'), '%Y/%m/%d')
        term_from = term_to - timedelta(days=1)
        if self._args.term_from:
            term_from = datetime.strptime(self._args.term_from, '%Y/%m/%d')

        if self._args.term_to:
            term_to = datetime.strptime(self._args.term_to, '%Y/%m/%d') + timedelta(days=1)

        if not self._args.all:
            sql = "{0} AND `Order`.updated_at BETWEEN '{1}' and '{2}'".format(sql, term_from, term_to)

        if self._args.delete:
            sql = "{0} AND `Order`.canceled_at IS NOT NULL".format(sql)
        else:
            sql = "{0} AND `Order`.canceled_at IS NULL".format(sql)
        return sql


class FileOperator(object):
    def __init__(self, args, spdb_info):
        self._args = args
        self.tmp_file_name = None
        self.tmp_file = None
        self.spdb_info = spdb_info

    @property
    def org(self):
        return self._args.org

    @property
    def org_name(self):
        org_dict = {
            '4': 'vissel',
            '15': 'rakutenticket',
            '24': 'eagles',
        }
        return org_dict[self._args.org]

    @property
    def term_str(self):
        date_fmt = '%Y/%m/%d'
        term_fmt = '%Y%m%d'
        term_to = datetime.strptime(datetime.now().date().strftime(date_fmt), date_fmt)
        term_from = term_to - timedelta(days=1)
        if self._args.term_from:
            term_from = datetime.strptime(self._args.term_from, date_fmt)

        term_str = datetime.strftime(term_from, term_fmt)
        if self._args.term_to:
            term_to = datetime.strptime(self._args.term_to, date_fmt)
            term_str = "{0}-{1}".format(datetime.strftime(term_from, term_fmt), datetime.strftime(term_to, term_fmt))
        return term_str

    @property
    def file_name(self):
        if self._args.delete:
            return "delete_{0}{1}.csv".format(self.org_name, self.term_str)
        return "delta_{0}{1}.csv".format(self.org_name, self.term_str)

    @property
    def gzip_file_name(self):
        if self._args.delete:
            return "delete_{0}{1}.csv.gz".format(self.org_name, self.term_str)
        return "delta_{0}{1}.csv.gz".format(self.org_name, self.term_str)

    @property
    def tmp_dir(self):
        return self.spdb_info.var_dir

    def open_tmp_file(self):
        self.tmp_file_name = os.path.join("{0}{1}.upload_file~".format(self.tmp_dir, uuid.uuid4()))
        self.tmp_file = open(self.tmp_file_name, 'w')

    def write_tmp_file(self, value):
        self.tmp_file.write(value)

    def close_tmp_file(self):
        if self.tmp_file:
            self.tmp_file.close()

    def upload(self, remote_path="/home/odin_ticket/from_ticket/"):
        upload_file_name = "{0}{1}".format(self.tmp_dir, self.file_name)
        upload_gzip_name = "{0}.gz".format(upload_file_name)
        os.rename(self.tmp_file_name, upload_file_name)

        with open(upload_file_name, 'rb') as f_in, gzip.open(upload_gzip_name, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

        if not self._args.local:
            ssh = SSHClient()
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(self.spdb_info.host, self.spdb_info.port, self.spdb_info.user, key_filename=self.spdb_info.private_key)
            sftp = ssh.open_sftp()
            sftp.put(upload_gzip_name, "{0}{1}".format(remote_path, self.gzip_file_name))
            sftp.close()
            ssh.close()

            if os.path.exists(upload_file_name):
                os.remove(upload_file_name)

            if os.path.exists(upload_gzip_name):
                os.remove(upload_gzip_name)


class SpdbInfo(object):
    def __init__(self, args):
        self._args = args
        self.conf = args.conf
        self.env = bootstrap(args.conf)
        self.settings = self.env['registry'].settings

    @property
    def host(self):
        return self.settings['spdb.host']

    @property
    def port(self):
        return int(self.settings['spdb.port'])

    @property
    def user(self):
        return self.settings['spdb.user']

    @property
    def private_key(self):
        return self.settings['spdb.private_key']

    @property
    def var_dir(self):
        return self.settings['spdb.var_dir']


def main():
    parser = argparse.ArgumentParser(description='SPDB')
    parser.add_argument('-o', '--org', required=True)
    parser.add_argument('-f', '--term_from')
    parser.add_argument('-t', '--term_to')
    parser.add_argument('-a', '--all')
    parser.add_argument('-d', '--delete')
    parser.add_argument('-l', '--local')
    parser.add_argument('-c', '--conf', required=True)
    args = parser.parse_args()

    setup_logging(args.conf)

    global spdb_sql
    sql_creater = SQLCreater(args, spdb_sql)
    file_operator = FileOperator(args, SpdbInfo(args))

    con = connect(host='dbmain.standby.altr', user='ticketing_ro', passwd='ticketing', db='ticketing', port=3308, charset='utf8', cursorclass=cursors.DictCursor)
    #con = connect(host='localhost', user='ticketing', passwd='ticketing', db='ticketing', port=3306, charset='utf8', cursorclass=cursors.DictCursor)
    file_operator.open_tmp_file()
    logger.info(u"SPDB start {0}".format(file_operator.file_name))

    try:
        cur = con.cursor()
        cur.execute(sql_creater.sql)
        orders = cur.fetchall()
        file_operator.write_tmp_file(u"PrimaryKey,予約番号,ステータス,支払いステータス,予約時間,ユーザID,イベントID,イベントタイトル,パフォーマンスID,パフォーマンス名,開演時間,商品明細名,席名,商品明細金額,商品明細個数,手数料,合計金額,authz_identifier,会員種別名,会員区分名,ポイント,支払い方法,引取方法,デバイス\n".encode('utf-8'))
        for row in orders:
            row = chop_none(row)
            file_operator.write_tmp_file(u"{0[PrimaryKey]},{0[order_no]},{0[order_status]},{0[payment_status]},{0[created_at]},{0[user_id]},{0[event_id]},{0[event_title]},{0[performance_id]},{0[performance_name]},{0[performance_start_on]},{0[product_item_name]},{0[seat_name]},{0[product_item_price]},{0[product_item_quantity]},{0[fee]},{0[total_amount]},{0[authz_identifier]},{0[membership_name]},{0[membergroup_name]},{0[point]},{0[payment_method]},{0[delivery_method]},{0[user_agent]}\n".format(row).encode('utf-8'))

        file_operator.close_tmp_file()
        file_operator.upload()
    except socket.error as e:
        logger.error(u"SPDB upload error.{0}".format(file_operator.file_name))

    finally:
        if con:
            con.close()
        file_operator.close_tmp_file()

    logger.info(u"SPDB end {0}".format(file_operator.file_name))


def chop_none(row):
    for val in row:
        if row[val] is None:
            row[val] = u''
    return row


if __name__ == '__main__':
    main()
