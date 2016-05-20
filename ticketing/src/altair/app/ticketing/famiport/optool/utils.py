# encoding: utf-8

import logging
from altair.app.ticketing.famiport.models import FamiPortReceiptType, FamiPortOrderType

logger = logging.getLogger(__name__)

class ValidateUtils(object):

    @classmethod
    def validate_rebook_cond(self, receipt, now):
        errors = []
        # キャンセル済みの場合
        if receipt.canceled_at is not None:
            logger.info('canceled receipt is not rebookable')
            errors.append(u'当予約はキャンセル済みです')
        # 申込ステータスが確定待ち出ない場合は処理不可
        if receipt.payment_request_received_at is None:
            logger.info('non paid(issued) receipt is not rebookable')
            errors.append(u'当予約は入金(発券)要求が未済です')
        # 申込ステータスが完了済みの場合は処理不可
        if receipt.completed_at is not None:
            logger.info('payment(ticketing) completed receipt is not rebookable')
            errors.append(u'当予約は入金(発券)完了済みです')
        # 支払期日が過ぎている場合は同席番再予約はできないようにするtkt1770
        if receipt.famiport_order.type != FamiPortOrderType.Ticketing.value and receipt.famiport_order.payment_due_at < now:
            logger.info('cannot rebook after payment due date is passed')
            errors.append(u'当予約は支払期日が過ぎているため同席番再予約できません')
        # TODO:期間バリデーション要追加
        # if receipt.get_refunds(self, request):
        #    refunds = receipt.get_refunds(self, request)
        #    return False

        return errors

    @classmethod
    def validate_reprint_cond(self, receipt, now):
        errors = []
        # キャンセル済みの場合
        if receipt.canceled_at is not None:
            logger.info('canceled receipt is not reprintable')
            errors.append(u'当予約はキャンセル済みです')
        # 払込レシートの場合
        if receipt.type == FamiPortReceiptType.Payment.value:
            logger.info('payment receipt is not reprintable')
            errors.append(u'当予約番号は払込のものです。発券用の番号でお試し下さい')
        # 期限超過の場合
        if receipt.type == FamiPortReceiptType.CashOnDelivery.value:
            if receipt.famiport_order.payment_due_at < now:
                logger.info('too late to reprint')
                errors.append(u'当予約は入金・発券期限を超過してます')
        else:
            if receipt.famiport_order.ticketing_end_at < now:
                logger.info('too late to reprint')
                errors.append(u'当予約は発券期限を超過してます')
        # 未発券の場合
        if receipt.payment_request_received_at is None:
            logger.info('non issued receipt is not reprintable')
            errors.append(u'当予約は未発券です')

        return errors
