# -*- coding:utf-8 -*-
"""90分自動確定処理

申込を行いPOSで入金を行わず30分VOID処理も行われない場合は
プレイガイド側で90分自動確定処理を行う
"""
import sys
import enum
import logging
import argparse
from datetime import (
    datetime,
    timedelta,
    )
from sqlalchemy import or_
from pyramid.paster import bootstrap, setup_logging
from pyramid.decorator import reify
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.famiport.models import (
    FamiPortOrder,
    FamiPortReceipt,
    )

logger = logging.getLogger(__file__)
LOCK_NAME = 'FAMIPORT_AUTO_COMPLETE'  # 多重起動防止用の名前


@enum.unique
class AutoCompleterStatus(enum.IntEnum):
    success = 0
    failure = 255  # その他エラー


def _get_now():
    return datetime.now()


class FamiPortOrderAutoCompleter(object):
    """POSで入金を行わず30分VOID処理も行われないFamiPortOrderを完了状態にしていく
    """
    def __init__(self, session, minutes=90, no_commit=False):
        self._session = session
        self._minutes = int(minutes)
        self._no_commit = no_commit  # commitするかどうか

    @reify
    def time_point(self):
        return _get_now() - timedelta(minutes=self._minutes)

    def complete(self):
        try:
            for receipt in self._fetch_target_famiport_receipts():
                self._do_complete(receipt)
                self._session.add(receipt)
        except Exception as err:
            logger.error(err)
            return AutoCompleterStatus.failuer.value
        else:
            if not self._no_commit:
                self._session.commit()
            return AutoCompleterStatus.success.value

    def _do_complete(self, receipt):
        """FamiPortOrderを完了状態にする"""
        receipt.rescued_at = self.time_point

    def _fetch_target_famiport_receipts(self):
        """対象のFamiPortOrderを取る"""
        return self._session \
                   .query(FamiPortReceipt) \
                   .filter(FamiPortReceipt.viod_at.is_(None)) \
                   .filter(FamiPortReceipt.rescued_at.is_(None)) \
                   .filter(or_(
                       FamiPortOrder.inquired_at.isnot(None),
                       FamiPortOrder.payment_request_received_at.isnot(None),
                       FamiPortOrder.customer_request_received_at.isnot(None),
                       ))  \
                   .filter(FamiPortReceipt.payment_request_received_at < self.time_point)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    if not args.stdout:
        setup_logging(args.config)
    env = bootstrap(args.config)
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')
    completer = FamiPortOrderAutoCompleter(session)
    try:
        with MultiStartLock(LOCK_NAME):
            return completer.complete()
    except AlreadyStartUpError as err:
        logger.warn('{}'.format(repr(err)))


if __name__ == u"__main__":
    sys.exit(main())
