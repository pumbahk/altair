# -*- coding:utf-8 -*-

#
# SEJ払戻ファイルをダウンロードして払戻状態を反映
#

import os
import sys
import logging
import argparse
from datetime import datetime, timedelta
from dateutil.parser import parse as parsedate

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.orm.exc import NoResultFound

from altair.app.ticketing.sej.scripts.sej_file_download import download, get_download_filename
from altair.app.ticketing.sej.scripts.sej_parse_file import process_files
from altair.app.ticketing.sej.models import _session, SejRefundEvent
from altair.app.ticketing.sej.file import parsers, SejFileReader, SejRefundFileParser
from altair.app.ticketing.sej.notification.models import SejNotificationType

logger = logging.getLogger(__name__)


def update_refund_status(in_filename, in_encoding='CP932'):
    in_file = open(in_filename)
    while True:
        parser = SejRefundFileParser(SejFileReader(in_file, encoding=in_encoding))
        if not parser.parse():
            break
        if len(parser.records) > 0:
            for record in parser.records:
                ticket_barcode_number = record.get('ticket_barcode_number')
                order_no = record.get('order_no')
                received_at = record.get('received_at')
                refund_status = record.get('refund_status')
                logger.info(u'ticket_barcode_number={0}, order_no={1}, refunded_at={2}'.format(
                    ticket_barcode_number,
                    order_no,
                    received_at
                    ))
                try:
                    refund_ticket = _session.query(SejRefundEvent).filter(
                        SejRefundEvent.order_no==order_no,
                        SejRefundEvent.ticket_barcode_number==ticket_barcode_number
                        ).one()
                    refund_ticket.refunded_at = received_at
                    refund_ticket.status = refund_status
                except NoResultFound as e:
                    logger.error(e.message)

def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config', metavar='config', type=str, help='config file')
    parser.add_argument('date', metavar='YYYYMMDD', type=str, help="target date")

    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']
    settings = env['registry'].settings

    logger.info(u'start sej_update_refund_status')
    logger.info(u'dates={}'.format(args.date))

    # 対象となる払戻イベントがあるならダウンロード
    target_date = parsedate(args.date)
    refund_events = _session.query(SejRefundEvent).filter(SejRefundEvent.start_at<=target_date, target_date<=SejRefundEvent.end_at).all()
    logger.info(u'SejRefundEvent start_at<={0}<=and end_at -> {1} records'.format(target_date, len(refund_events)))

    processed_shops = set()
    for refund_event in refund_events:
        logger.info(u'shop_id={}'.format(refund_event.shop_id))
        if refund_event.shop_id in processed_shops:
            logger.info(u'already downloaded')
            continue

        # 払戻結果ファイルをダウンロード
        files = download(request,
                         None,
                         refund_event.shop_id,
                         settings.get('sej.api_key'),
                         settings.get('sej.inticket_api_url'),
                         SejNotificationType.FileInstantRefundInfo.v,
                         args.date,
                         settings.get('altair.sej.refund_result.data_dir'))
        logger.info(u'download file={}'.format(files))

        # 払戻結果を反映
        for file in files:
            update_refund_status(file)

        # csv形式でバックアップしておく
        process_files(SejNotificationType.FileInstantRefundInfo.v, files)
        processed_shops.add(refund_event.shop_id)

    logger.info(u'end sej_update_refund_status')
    return


if __name__ == u"__main__":
    sys.exit(main(sys.argv))
