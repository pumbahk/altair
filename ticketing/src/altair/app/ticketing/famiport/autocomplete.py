# cencoding: utf-8
"""90分自動確定処理

- 申込を行いPOSで入金を行わず30分VOID処理も行われない場合はプレイガイド側で90分自動確定処理を行う
- 確定したものはメールを送信する
"""
import re
import enum
import logging
from zope.interface import implementer
from datetime import (
    datetime,
    timedelta,
    )
from sqlalchemy.orm.exc import (
    NoResultFound,
    MultipleResultsFound,
    )
from pyramid.decorator import reify
from pyramid.renderers import render
from altair.mailhelpers import Mailer
from altair.app.ticketing.famiport.models import (
    FamiPortShop,
    FamiPortReceipt,
    FamiPortReceiptType,
    )
from .interfaces import IFamiPortOrderAutoCompleter

_logger = logging.getLogger(__file__)


@enum.unique
class AutoCompleterStatus(enum.IntEnum):
    success = 0
    failure = 255  # その他エラー


def _get_now():
    return datetime.now()


class FamiPortAutoCompleteError(Exception):
    pass


class NoSuchReceiptError(FamiPortAutoCompleteError):
    pass


class InvalidMailSubjectError(FamiPortAutoCompleteError):
    u"""メールのsubjectの設定がおかしい"""


class InvalidMailAddressError(FamiPortAutoCompleteError):
    u"""メールアドレスの設定がおかしい"""


class InvalidReceiptStatusError(FamiPortAutoCompleteError):
    u"""FamiPortReceiptの状態がおかしい"""


class InvalidReceiptTypeError(FamiPortAutoCompleteError):
    u"""FamiPortReceiptのtypeがおかしい"""


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
    def total_amount(self):
        return self._famiport_order.total_amount

    @reify
    def classifier(self):
        type_ = self._receipt.type
        if type_ == FamiPortReceiptType.Payment.value:
            return u'前払'
        elif type_ == FamiPortReceiptType.Ticketing.value:
            return u'代済発券または前払い後日発券'
        elif type_ == FamiPortReceiptType.CashOnDelivery.value:
            return u'代引'
        else:
            raise InvalidReceiptTypeError(
                'invalid famiport receipt type: FamiPortReceipt.type={}'.format(type_))

    @reify
    def issued_at(self):
        if self._famiport_order.issued_at:
            return unicode(self._receipt.famiport_order.issued_at.strftime('%Y/%m/%d %H:%M:%S'))  # noqa
        else:
            return ''

    @reify
    def shop_code(self):
        return self._receipt.shop_code

    @reify
    def shop_name(self):
        shop = self._session.query(FamiPortShop).filter_by(code=self.shop_code).first()
        return shop.name if shop else ''

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

    def __init__(self, registry, recipients=None):
        self._registry = registry
        self._recipients = recipients

    def get_setup_errors(self):
        try:
            self.create_subject(_get_now())
            self.recipients
        except FamiPortAutoCompleteError as err:
            _logger.error('famiport notifier setup error: {}'.format(err))
            return [err]
        else:
            return []

    def get_mailer(self):
        return Mailer(self.settings)

    def notify(self, now_, **kwds):
        """送信処理"""
        mailer = self.get_mailer()
        mailer.create_message(
            sender=self.sender,
            recipient=', '.join(self.recipients),
            subject=self.create_subject(now_),
            body=self.create_body(**kwds),
            )
        mailer.send(self.sender, self.recipients)
        _logger.info('send ok famiport auto complete mail')

    @reify
    def sender(self):
        try:
            return self.settings['altair.famiport.mail.sender']
        except KeyError:
            raise InvalidMailAddressError()

    @reify
    def settings(self):
        return self._registry.settings

    @reify
    def recipients(self):
        if isinstance(self._recipients, (list, tuple, set)):
            return self._recipients
        elif self._recipients is None:
            try:
                recipients = self.settings['altair.famiport.mail.recipients']
                recipients = [recipient.strip() for recipient in re.split(ur'\s*,\s*|\s+', recipients)]
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

    def create_subject(self, now_):
        fmt = ''
        try:
            fmt = self.settings['altair.famiport.mail.subject']
        except KeyError as err:
            raise InvalidMailSubjectError('invalid mail subject: {}'.format(err))
        fmt = fmt.strip()
        if fmt:
            return now_.strftime(fmt).decode('utf8')
        else:
            raise InvalidMailSubjectError('invalid mail subject(blank)')
        return self._time_point.strftime(fmt).decode('utf8')

    def create_body(self, **kwds):
        return render(self.template_path, kwds)


@implementer(IFamiPortOrderAutoCompleter)
class FamiPortOrderAutoCompleter(object):
    """POSで入金を行わず30分VOID処理も行われないFamiPortOrderを完了状態にしていく
    """
    def __init__(self, registry, no_commit=False, recipients=None, notifier=None):
        self._registry = registry
        self._no_commit = no_commit  # commitするかどうか
        self._recipients = recipients
        self._notifier = notifier
        if self._notifier is None:
            self._notifier = FamiPortOrderAutoCompleteNotifier(
                self._registry, self._recipients)

    def get_setup_errors(self):
        return self._notifier.get_setup_errors()

    def complete(self, session, receipt_id, now_=None):
        """FamiPortReceiptを90VOID救済する

        no_commitが指定されていない場合はDBへのcommitをしません。
        救済できないFamiPortReceiptを指定した場合はInvalidReceiptStatusErrorを送出します。
        """
        if now_ is None:
            now_ = _get_now()

        receipt = self._get_receipt(session, receipt_id)
        if receipt is None:
            raise NoSuchReceiptError('%d' % receipt_id)
        if receipt.can_auto_complete(now_):
            _logger.debug('completing: FamiPortReceipt.id={}'.format(receipt.id))
            self._do_complete(session, receipt, now_)
            if not self._no_commit:
                session.add(receipt)
                session.commit()
                self._notify(session, receipt, now_)
        else:   # statusの状態がおかしい
            _logger.debug('invalid status: FamiPortReceipt.id={}'.format(receipt.id))
            raise InvalidReceiptStatusError(
                'invalid receipt status: FamiPortReceipt.id={}'.format(receipt.id))

    def _notify(self, session, receipt, now_):
        from pyramid.threadlocal import get_current_request
        context = FamiPortOrderAutoCompleteNotificationContext(
            request=get_current_request(),
            session=session,
            receipt=receipt,
            time_point=now_,
            )
        self._notifier.notify(data=context, now_=now_)

    def _do_complete(self, session, receipt, now_):
        """FamiPortOrderを完了状態にする"""
        receipt.rescued_at = now_
        receipt.completed_at = now_

    def _get_receipt(self, session, receipt_id):
        """FamiPortReceiptを取得する"""
        try:
            return session \
                       .query(FamiPortReceipt) \
                       .filter_by(id=receipt_id) \
                       .one()
        except NoResultFound:
            return None
        except MultipleResultsFound:
            return None


class FamiPortOrderAutoCompleteRunner(object):
    def __init__(self, registry, delta):
        self._registry = registry
        self._delta = delta
        self._completer = self._registry.queryUtility(IFamiPortOrderAutoCompleter)
        if self._completer is None:
            raise FamiPortAutoCompleteError('completer not found')

    def get_setup_errors(self):
        return self._completer.get_setup_errors()

    @reify
    def time_point(self):
        return _get_now() - self._delta

    def complete_all(self, session):
        success_receipt_ids = []
        failed_receipt_ids = []
        for receipt_value in self._fetch_target_famiport_receipt_ids(session):
            receipt_id = receipt_value.id
            try:
                self._completer.complete(session, receipt_id, self.time_point)
            except InvalidReceiptStatusError as err:
                _logger.error(err)
                failed_receipt_ids.append(receipt_id)
            else:
                success_receipt_ids.append(receipt_id)
        return success_receipt_ids, failed_receipt_ids

    def _fetch_target_famiport_receipt_ids(self, session):
        """対象のFamiPortOrderを取る"""
        return session \
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
