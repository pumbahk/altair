# -*- coding:utf-8 -*-
"""90分自動確定処理

- 申込を行いPOSで入金を行わず30分VOID処理も行われない場合はプレイガイド側で90分自動確定処理を行う
- 確定したものはメールを送信する

メールアドレスは次の順序で取得する
----------------------------------

1. コマンドラインパラメータ
2. 設定ファイル

設定されていなければエラー終了する。

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
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from pyramid.paster import bootstrap, setup_logging
from pyramid.decorator import reify
from pyramid.renderers import render_to_response
from pyramid.threadlocal import get_current_request
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.core.models import Mailer
from altair.app.ticketing.famiport.models import (
    FamiPortOrder,
    FamiPortReceipt,
    )

_logger = logging.getLogger(__file__)
LOCK_NAME = 'FAMIPORT_AUTO_COMPLETE'  # 多重起動防止用の名前


@enum.unique
class AutoCompleterStatus(enum.IntEnum):
    success = 0
    failure = 255  # その他エラー


def _get_now():
    return datetime.now()


class InvalidMailAddressError(Exception):
    u"""メールアドレスの設定がおかしい"""


class InvalidReceiptStatusError(Exception):
    u"""FamiPortReceiptの状態がおかしい"""


class FamiPortOrderAutoCompleteNotifier(object):
    template_path = u'altair.app.ticketing:templates/famport/famport_auto_complete.txt'

    def __init__(self, request, session, recipients=None):
        self._request = request
        self._session = session
        self._recipients = recipients

    def get_mailer(self):
        return Mailer(self.settings)

    def notify(self, **kwds):
        mailer = self.get_mailer()
        mailer.create_message(
            sender=self.sender,
            recipient=', '.join(self.recipients),
            subject=self.subject,
            body=self.create_body(**kwds),
            )
        mailer.send(self.sender, self.mailaddrs)

    @reify
    def sender(self):
        return u'dev@ticketstar.jp'

    @reify
    def settings(self):
        return self._request.registry.settings

    @reify
    def recipients(self):
        if isinstance(self._recipients, [list, tuple, set]):
            return self._recipients
        elif self._recipients is None:
            try:
                recipients = self.settings['famiport.mail.recipients']
                recipients = recipients.split(',')
                if recipients:
                    return recipients
            except KeyError as err:
                raise InvalidMailAddressError('no stting')  # 設定なし
            except Exception as err:
                raise InvalidMailAddressError('invalid stting: {}'.format(err))  # おかしな状態
        else:
            raise InvalidMailAddressError('Invalid mail address: {}'.format(repr(self._mailaddrs)))

    @reify
    def subject(self):
        return u'90分VOIDバッチにより確定状態になりました'

    def create_body(self, **kwds):
        return render_to_response(self.template_path, kwds)


class FamiPortOrderAutoCompleter(object):
    """POSで入金を行わず30分VOID処理も行われないFamiPortOrderを完了状態にしていく
    """
    def __init__(self, request, session, minutes=90, no_commit=False, recipients=None):
        self._request = request
        self._session = session
        self._minutes = int(minutes)
        self._no_commit = no_commit  # commitするかどうか
        self._recipients = recipients
        self._notifier = FamiPortOrderAutoCompleteNotifier(
            self._request, self._session, self._recipients)

    @reify
    def time_point(self):
        return _get_now() - timedelta(minutes=self._minutes)

    def complete(self, receipt_id):
        """FamiPortReceiptを90VOID救済する

        no_commitが指定されていない場合はDBへのcommitをしません。
        救済できないFamiPortReceiptを指定した場合はInvalidReceiptStatusErrorを送出します。
        """
        receipt = self._get_receipt(receipt_id)
        if receipt.can_auto_complete(self.time_point):
            self._do_complete(receipt)
            if not self._no_commit:
                self._session.add(receipt)
                self._session.commit()
        else:   # statusの状態がおかしい
            raise InvalidReceiptStatusError(
                'invalid receipt status: FamiPortReceipt.id={}'.format(receipt_id))

    def complete_all(self):
        success_receipt_ids = []
        failed_receipt_ids = []
        for receipt_id in self._fetch_target_famiport_receipt_ids():
            try:
                self.complete(receipt_id)
            except InvalidReceiptStatusError as err:
                _logger.error(err)
                failed_receipt_ids.append(receipt_id)
            else:
                success_receipt_ids.append(receipt_id)
        return success_receipt_ids, failed_receipt_ids

    def _do_complete(self, receipt):
        """FamiPortOrderを完了状態にする"""
        receipt.rescued_at = self.time_point
        receipt.completed_at = self.time_point

    def _get_receipt(self, receipt_id):
        """FamiPortReceiptを取得する"""
        try:
            return self._session \
                       .query(FamiPortReceipt) \
                       .filter_by(id=receipt_id) \
                       .one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            return None

    def _fetch_target_famiport_receipt_ids(self):
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
                   .filter(FamiPortReceipt.payment_request_received_at < self.time_point) \
                   .with_entities(FamiPortReceipt.id)


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('--to', default=None)
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    if not args.stdout:
        setup_logging(args.config)

    recipients = None
    if args.to:
        recipients = args.split(',')

    env = bootstrap(args.config)
    request = get_current_request()
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')
    completer = FamiPortOrderAutoCompleter(request, session, recipients)
    try:
        with MultiStartLock(LOCK_NAME):
            return completer.complete_all()
    except AlreadyStartUpError as err:
        _logger.warn('{}'.format(repr(err)))


if __name__ == u"__main__":
    sys.exit(main())
