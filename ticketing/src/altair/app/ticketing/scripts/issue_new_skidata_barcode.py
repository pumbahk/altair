#! /usr/bin/env python
# -*- coding:utf-8 -*-
import argparse
import csv
import logging
import transaction
from altair.app.ticketing.skidata.models import SkidataBarcode
from pyramid.paster import bootstrap

logger = logging.getLogger(__name__)
csv_header = [u'skidata_barcode_id', u'qr_content']


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', metavar='config', type=str, required=True)
    parser.add_argument('-n', '--number', metavar='number', type=int, required=True)
    parser.add_argument('-o', '--output_csv_name', metavar='output_csv_name', type=str, required=True)

    args = parser.parse_args()
    bootstrap(args.config)

    logger.info(u'Starting to issue {} SkidataBarcode.'.format(args.number))
    export_rows = list()
    try:
        for _ in range(args.number):
            new_barcode = SkidataBarcode.insert_new_barcode(token_id=None)
            transaction.commit()  # 競合によりQRデータが衝突するとインサート失敗するので一件ずつコミット
            export_rows.append([new_barcode.id, new_barcode.data])
    except Exception as e:
        logger.exception(e)
    finally:
        transaction.abort()

    if len(export_rows) == 0:
        logger.error(u'Failed to issue SkidataBarcode.')
        return
    if len(export_rows) == args.number:
        logger.info(u'Finished to issue {} SkidataBarcode'.format(args.number))
    if len(export_rows) < args.number:
        logger.warn(u'Finished to to issue partial SkidataBarcode: {}/{}.'.format(len(export_rows), args.number))

    with open(args.output_csv_name, 'w') as f:
        csv_writer = csv.writer(f)
        csv_writer.writerow(csv_header)
        for row in export_rows:
            csv_writer.writerow(row)
    logger.info(u'Exported SkidataBarcode to {}.'.format(args.output_csv_name))


if __name__ == '__main__':
    main()
