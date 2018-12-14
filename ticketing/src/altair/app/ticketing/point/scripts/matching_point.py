# -*- coding: utf-8 -*-
import argparse
import logging
import sys

from pyramid.paster import setup_logging, bootstrap
from datetime import datetime, timedelta
from altair.app.ticketing.models import DBSession
from ..models import PointRedeem
from sqlalchemy import or_

logger = logging.getLogger(__name__)

# ポイントステータス
POINT_STATUS_AUTH = '0'
POINT_STATUS_FIX = '1'
POINT_STATUS_CANCEL = '1'


def main():
    parser = argparse.ArgumentParser(add_help=True)
    parser.add_argument('-g', '--group_id', required=True)
    parser.add_argument('-r', '--reason_id', required=True)
    parser.add_argument('-d', '--date', help='date format : YYYY-mm-dd (sample : 2018-11-14)')
    parser.add_argument('-c', '--config', required=True, help='Please provide altair.ticketing.batch.ini')
    args = parser.parse_args()

    setup_logging(args.config)
    bootstrap(args.config)

    # dateがパラメータに存在する場合は指定日を、存在しない場合は前日の日付をセットする
    today = datetime.now()
    from_date = (today - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    if args.date is not None:
        str_date = '{args_date} 00:00:00'.format(args_date=args.date)
        from_date = datetime.strptime(str_date, '%Y-%m-%d %H:%M:%S')

    to_date = from_date + timedelta(days=1)

    """
    authステータスの突合せ対象抽出
    - authed_at   : from_dateの日付
    - fixed_at    : to_date以降の日付 or NULL
    - canceled_at : to_date以降の日付 or NULL
    - deleted_at  : NULL
    group_id, reason_idはバッチ起動時に指定した値で検索する
    """
    auth_query = DBSession.query(PointRedeem)\
        .filter(PointRedeem.authed_at >= from_date)\
        .filter(PointRedeem.authed_at < to_date)\
        .filter(or_(PointRedeem.fixed_at >= to_date, PointRedeem.fixed_at.is_(None)))\
        .filter(or_(PointRedeem.canceled_at >= to_date, PointRedeem.canceled_at.is_(None)))\
        .filter(PointRedeem.group_id == args.group_id)\
        .filter(PointRedeem.reason_id == args.reason_id)

    auth_point_redeems = auth_query.all()
    logger.info('number of auth target: {len_auth_point_redeems}'
                .format(len_auth_point_redeems=len(auth_point_redeems)))
    for auth in auth_point_redeems:
        cols = [
            str(auth.unique_id),
            '0',
            POINT_STATUS_AUTH,
            str(auth.auth_point),
            str(auth.authed_at),
            ''
        ]
        sys.stdout.write(u'\t'.join(cols).encode('utf-8'))
        sys.stdout.write("\n")

    """
    fixステータスの突合せ対象抽出
    - fixed_at    : from_dateの日付
    - canceled_at : to_date以降の日付 or NULL
    - deleted_at  : NULL
    group_id, reason_idはバッチ起動時に指定した値で検索する
    """
    fix_query = DBSession.query(PointRedeem)\
        .filter(PointRedeem.fixed_at >= from_date)\
        .filter(PointRedeem.fixed_at < to_date)\
        .filter(or_(PointRedeem.canceled_at >= to_date, PointRedeem.canceled_at.is_(None)))\
        .filter(PointRedeem.group_id == args.group_id) \
        .filter(PointRedeem.reason_id == args.reason_id)

    fix_point_redeems = fix_query.all()
    logger.info('number of fix target: {len_fix_point_redeems}'
                .format(len_fix_point_redeems=len(fix_point_redeems)))
    for fix in fix_point_redeems:
        cols = [
            str(fix.unique_id),
            '0',
            POINT_STATUS_FIX,
            str(fix.fix_point),
            str(fix.fixed_at),
            ''
        ]
        sys.stdout.write(u'\t'.join(cols).encode('utf-8'))
        sys.stdout.write("\n")

    """
    cancelステータスの突合せ対象抽出
    - canceled_at : from_dateの日付
    - deleted_at  : NULL
    group_id, reason_idはバッチ起動時に指定した値で検索する
    """
    cancel_query = DBSession.query(PointRedeem)\
        .filter(PointRedeem.canceled_at >= from_date)\
        .filter(PointRedeem.canceled_at < to_date)\
        .filter(PointRedeem.group_id == args.group_id)\
        .filter(PointRedeem.reason_id == args.reason_id)

    cancel_point_redeems = cancel_query.all()
    logger.info('number of cancel target: {len_cancel_point_redeems}'
                .format(len_cancel_point_redeems=len(cancel_point_redeems)))
    for cancel in cancel_point_redeems:
        cols = [
            str(cancel.unique_id),
            '0',
            POINT_STATUS_CANCEL,
            str(cancel.fix_point),
            str(cancel.canceled_at),
            ''
        ]
        sys.stdout.write(u'\t'.join(cols).encode('utf-8'))
        sys.stdout.write("\n")
