# -*- coding:utf-8 -*-

import os
import sys
import logging
import transaction
import argparse
import requests
from requests.auth import HTTPBasicAuth

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy import and_
from sqlalchemy.sql.expression import not_
import sqlahelper

from altair.app.ticketing.sej.ticket import create_refund_zip_file
from altair.app.ticketing.sej.nwts import nws_data_send
from altair.app.ticketing.sej.models import _session

def send_refund_file(session):
    ''' 払戻ファイルをSEJへ送信
    '''
    config_file = sys.argv[1]
    log_file = os.path.abspath(sys.argv[2])
    logging.config.fileConfig(log_file)
    app_env = bootstrap(config_file)
    settings = app_env['registry'].settings

    logging.info('start send_refund_file batch')

    try:
        # 払戻対象データをファイルに書き出して圧縮
        zip_file = create_refund_zip_file(_session)

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
    finally:
        _session.commit()
    logging.info('end send_refund_file batch')

def send_refund_file_with_proxy(session=None):
    ''' 払戻ファイルをプロキシ経由でSEJへ送信
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('config')
    args = parser.parse_args()

    setup_logging(args.config)
    env = bootstrap(args.config)
    settings = env['registry'].settings

    if session is None:
        session = _session

    logging.info('start send_refund_file_with_proxy batch')
    try:
        create_and_send_refund_file(settings, _session)
    finally:
        session.commit()
    logging.info('end send_refund_file_with_proxy batch')

def create_and_send_refund_file(settings, session=None):
    if session is None:
        session = _session

    nwts_proxy_url = settings.get('altair.sej.nwts.proxy_url')
    if nwts_proxy_url is None:
        logging.warning("altair.sej.nwts.proxy_url is not given. using deprecated sej.nwts.proxy_url instead")
        nwts_proxy_url = settings['sej.nwts.proxy_url']

    nwts_auth_user = settings.get('altair.sej.nwts.auth_user')
    if nwts_auth_user is None:
        logging.warning("altair.sej.nwts.auth_user is not given. using deprecated sej.nwts.auth_user instead")
        nwts_auth_user = settings['sej.nwts.auth_user']

    nwts_auth_pass = settings.get('altair.sej.nwts.auth_password')
    if nwts_auth_pass is None:
        logging.warning("altair.sej.nwts.auth_password is not given. using deprecated sej.nwts.auth_pass instead")
        nwts_auth_pass = settings['sej.nwts.auth_pass']

    # 払戻対象データをファイルに書き出して圧縮
    try:
        zip_file = create_refund_zip_file(session)
    finally:
        session.commit()

    # 払戻対象データをSEJへ送信
    if zip_file:
        logging.info('zipfile=%s' % zip_file)
        try:
            files = {'zipfile': (os.path.basename(zip_file), open(zip_file, 'rb'))}
            r = requests.post(
                url=nwts_proxy_url,
                files=files,
                auth=HTTPBasicAuth(nwts_auth_user, nwts_auth_pass)
            )
            if r.status_code == 200:
                logging.info('success')
            else:
                logging.error('proxy response = %s' % r.status_code)
        except Exception:
            logging.exception('exception occured')


if __name__ == '__main__':
    send_refund_file_with_proxy()
