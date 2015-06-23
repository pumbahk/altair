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
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from pyramid.paster import bootstrap, setup_logging
from pyramid.decorator import reify
from pyramid.renderers import render
from pyramid.threadlocal import get_current_request
from altair.multilock import (
    MultiStartLock,
    AlreadyStartUpError,
    )
from altair.sqlahelper import get_global_db_session
from altair.app.ticketing.core.models import Mailer
from altair.app.ticketing.famiport.models import FamiPortReceipt

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


class FamiPortOrderAutoCompleteNotificationContext(object):
    def __init__(self, request, session, receipt, time_point):
        self._request = request
        self._session = session
        self._receipt = receipt
        self._time_point = time_point

    @reify
    def _famiport_order(self):
        return self._receipt.famiport_order

    @reify
    def _famiport_sales_segment(self):
        return self._famiport_order.famiport_sales_segment

    @reify
    def _famiport_performance(self):
        return self._famiport_sales_segment.famiport_performance

    @reify
    def _famiport_event(self):
        return self._famiport_performance.famiport_event

    @reify
    def _famiport_client(self):
        return self._famiport_order.famiport_client

    @reify
    def _famiport_playguide(self):
        return self._famiport_client.playguide

    @reify
    def time_point(self):
        return self._time_point.strftime('%Y/%m/%d %H:%M:%S')

    @reify
    def reserve_number(self):
        return self._receipt.reserve_number

    @reify
    def barcode_no(self):
        return self._receipt.barcode_no

    @reify
    def order_identifier(self):
        return self._receipt.famiport_order_identifier

    @reify
    def order_ticket_no(self):
        return u'???'

    @reify
    def exchange_ticket_no(self):
        return u'???'

    @reify
    def total_amount(self):
        return self._famiport_order.total_amount

    @reify
    def classifier(self):
        return u'???'

    @reify
    def issued_at(self):
        if self._famiport_order.issued_at:
            return unicode(self._receipt.famiport_order.issued_at.strftime('%Y/%m/%d %H:%M:%S'))
        else:
            return ''

    @reify
    def shop_code(self):
        return self._receipt.shop_code

    @reify
    def shop_name(self):
        return u'???'

    @reify
    def event_code_1(self):
        return self._famiport_event.code_1

    @reify
    def event_code_2(self):
        return self._famiport_event.code_2

    @reify
    def event_name_1(self):
        return self._famiport_event.name_1

    @reify
    def event_name_2(self):
        return self._famiport_event.name_2

    @reify
    def performance_name(self):
        return self._famiport_performance.name

    @reify
    def performance_code(self):
        return self._famiport_performance.code

    @reify
    def playguide_code(self):
        return self._famiport_playguide.discrimination_code


class FamiPortOrderAutoCompleteNotifier(object):
    template_path = u'altair.app.ticketing:templates/famiport/famiport_auto_complete.txt'

    def __init__(self, request, session, recipients=None, time_point=None):
        self._request = request
        self._session = session
        self._recipients = recipients
        self._time_point = time_point

    def get_mailer(self):
        return Mailer(self.settings)

    def notify(self, **kwds):
        """送信処理"""
        mailer = self.get_mailer()
        mailer.create_message(
            sender=self.sender,
            recipient=', '.join(self.recipients),
            subject=self.subject,
            body=self.create_body(**kwds),
            )
        mailer.send(self.sender, self.recipients)
        _logger.info('send ok famiport auto complete mail')

    @reify
    def sender(self):
        return u'dev@ticketstar.jp'

    @reify
    def settings(self):
        return self._request.registry.settings

    @reify
    def recipients(self):
        if isinstance(self._recipients, (list, tuple, set)):
            return self._recipients
        elif self._recipients is None:
            try:
                recipients = self.settings['altair.famiport.mail.recipients']
                recipients = recipients.split(',')
                if recipients:
                    return recipients
                else:
                    raise InvalidMailAddressError('no setting')  # 設定なし
            except KeyError as err:
                raise InvalidMailAddressError('no setting')  # 設定なし
            except Exception as err:
                raise InvalidMailAddressError('invalid stting: {}'.format(err))  # おかしな状態

        else:
            raise InvalidMailAddressError('Invalid mail address: {}'.format(repr(self._mailaddrs)))

    @reify
    def subject(self):
        return u'【TicketStar　Famiポート90分確定取引】送信日時（{}）'.format(
            self._time_point.strftime('%Y/%m/%d %H:%M:%S'))

    def create_body(self, **kwds):
        return render(self.template_path, kwds)


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
            self._request, self._session, self._recipients, time_point=self.time_point)

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
            _logger.debug('completing: FamiPortReceipt.id={}'.format(receipt.id))
            self._do_complete(receipt)
            if not self._no_commit:
                self._session.add(receipt)
                self._session.commit()
            self._notify(receipt)
        else:   # statusの状態がおかしい
            _logger.debug('invalid status: FamiPortReceipt.id={}'.format(receipt.id))
            raise InvalidReceiptStatusError(
                'invalid receipt status: FamiPortReceipt.id={}'.format(receipt_id))

    def _notify(self, receipt):
        context = FamiPortOrderAutoCompleteNotificationContext(
            request=self._request,
            session=self._session,
            receipt=receipt,
            time_point=self.time_point,
            )
        self._notifier.notify(data=context)

    def complete_all(self):
        success_receipt_ids = []
        failed_receipt_ids = []
        for receipt_value in self._fetch_target_famiport_receipt_ids():
            receipt_id = receipt_value.id
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
                   .filter(FamiPortReceipt.inquired_at.isnot(None)) \
                   .filter(FamiPortReceipt.payment_request_received_at.isnot(None)) \
                   .filter(FamiPortReceipt.payment_request_received_at.isnot(None)) \
                   .filter(FamiPortReceipt.completed_at.is_(None)) \
                   .filter(FamiPortReceipt.void_at.is_(None)) \
                   .filter(FamiPortReceipt.canceled_at.is_(None)) \
                   .filter(FamiPortReceipt.rescued_at.is_(None)) \
                   .filter(FamiPortReceipt.payment_request_received_at < self.time_point) \
                   .with_entities(FamiPortReceipt.id) \
                   .all()


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--stdout', default=False, action='store_true')
    parser.add_argument('--recipients', default=None)
    parser.add_argument('--no-commit', default=None, action='store_true')
    parser.add_argument('-C', '--config', metavar='config', type=str, dest='config', required=True, help='config file')
    args = parser.parse_args(argv)

    if not args.stdout:
        setup_logging(args.config)

    recipients = None
    if args.recipients:
        recipients = args.recipients.split(',')

    env = bootstrap(args.config)
    request = get_current_request()
    registry = env['registry']
    session = get_global_db_session(registry, 'famiport')
    completer = FamiPortOrderAutoCompleter(request, session, no_commit=args.no_commit, recipients=recipients)
    _logger.info('famiport auto complete start')
    try:
        with MultiStartLock(LOCK_NAME):
            _logger.info('get a multiple lock')
            return completer.complete_all()
    except AlreadyStartUpError as err:
        _logger.warn('{}'.format(repr(err)))
    _logger.info('famiport auto complete end')

if __name__ == u"__main__":
    sys.exit(main())
