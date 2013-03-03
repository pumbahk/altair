# -*- coding:utf-8 -*-

import os
import sys
import logging
import transaction

from pyramid.paster import bootstrap
from sqlalchemy import and_
from sqlalchemy.sql.expression import not_
import sqlahelper

from ticketing.sej.ticket import create_refund_zip_file
from ticketing.sej.nwts import nws_data_send

def send_refund_file():
    ''' 払戻ファイルをSEJへ送信
    '''
    config_file = sys.argv[1]
    log_file = os.path.abspath(sys.argv[2])
    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    settings = app_env['registry'].settings

    logging.info('start send_refund_file batch')

    # 払戻対象データをファイルに書き出して圧縮
    zip_file = create_refund_zip_file()

    # 払戻対象データをSEJへ送信
    nws_data_send(
        url=settings.get('sej.nwts.url') + '/tpayback.asp',
        data=open(zip_file).read(),
        file_id='SEIT020U',
        terminal_id=settings.get('sej.terminal_id'),
        password=settings.get('sej.password'),
        ca_certs=settings.get('sej.nwts.ca_certs'),
        cert_file=settings.get('sej.nwts.cert_file'),
        key_file=settings.get('sej.nwts.key_file')
    )

    logging.info('end send_refund_file batch')


if __name__ == '__main__':
    send_refund_file()
