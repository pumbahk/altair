# -*- coding: utf-8 -*-

import logging
import sys
import argparse
from pyramid.paster import bootstrap, setup_logging

from .reports import SalesReporterOrderPrice, S3SalesReportOutputer, CsvSalesReportOutputer

logger = logging.getLogger(__name__)

# イーグルスの売上げレポートのバッチ用
REPORT_TARGET_ORG_ID = 24


def main(argv=sys.argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    request = env['request']

    logger.info('start send_sales_report_order_price batch')

    reporter = SalesReporterOrderPrice(request, S3SalesReportOutputer(request, request.registry.settings[
        'sales_reports.var_dir']), REPORT_TARGET_ORG_ID)
    reporter.output_report()

    reporter.create_report_data(True)
    reporter.output_report(True)

    logger.info('end send_sales_report_order_price batch')


if __name__ == '__main__':
    main()
