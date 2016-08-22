# encoding: utf-8

import logging
from altair.app.ticketing.famiport.models import FamiPortReceiptType, FamiPortOrderType
from . import AES_SECRET_KEY
from Crypto.Cipher import AES
from Crypto import Random

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

def encrypt_password(password, existed_password=None):
    import hashlib, six
    from os import urandom
    salt = existed_password[0:32] if existed_password \
        else u''.join('%02x' % six.byte2int(c) for c in urandom(16))

    h = hashlib.sha256()
    h.update(salt + password)
    password_digest = h.hexdigest()
    return salt + password_digest

class AESEncryptor(object):

    @classmethod
    def _is_token_expried(self, created_at_str):
        from datetime import datetime, timedelta
        created_at = datetime.strptime(created_at_str, "%Y%m%d%H%M")
        now = datetime.now()
        # 発行したパスワードを変更するURLの有効期限は3時間
        return now > created_at + timedelta(hours=3)

    def _build_encrypting_str(self, user_id):
        # キーを作成するタイミングの情報を作成
        from datetime import datetime
        created_at = datetime.now().strftime("%Y%m%d%H%M")

        # ユーザIDを文字列にする
        user_id_str = str(user_id)

        user_id_time_str = user_id_str + created_at

        # AESの暗号化が16(32) byteの文字列しか暗号化できないため、長さが16の文字列にする。
        return ''.join(['0'] * (16 - len(user_id_time_str))) + user_id_time_str

    @classmethod
    def get_cipher(cls, iv=None):
        if not iv:
            iv = Random.new().read(AES.block_size)
        cipher = AES.new(AES_SECRET_KEY, AES.MODE_CFB, iv)
        return cipher, iv

    @classmethod
    def verify_token(cls, token):
    # tokenを復号して、ユーザID情報を返す。
        try:
            token = token.decode('hex')
            iv = token[:16]
            cipher, _ = cls.get_cipher(iv)
            user_id_time_str = cipher.decrypt(token[16:])
            user_id = user_id_time_str[0:4]
            created_at_str = user_id_time_str[4:]

            if not cls._is_token_expried(created_at_str):
                return int(user_id)
            else:
                return None
        except (ValueError, TypeError):
            return None

    def get_token(self, user_id):
    # ユーザIDを使って暗号化する。
        if not user_id:
            return None

        user_id_time_str = self._build_encrypting_str(user_id)
        cipher, iv = self.get_cipher()
        token = iv + cipher.encrypt(user_id_time_str)
        return token.encode('hex')

def sendmail(settings, recipient, subject, html):
    from altair.mailhelpers import Mailer
    sender = settings['mail.message.sender']
    mailer = Mailer(settings)
    mailer.create_message(
        sender = sender,
        recipient = recipient,
        subject = subject,
        body = '',
        html = html.text,
        encoding='utf-8'
    )
    try:
        mailer.send(sender, recipient)
        return True
    except Exception, e:
        logging.error(u'メール送信失敗 %s' % e.message)
        return False