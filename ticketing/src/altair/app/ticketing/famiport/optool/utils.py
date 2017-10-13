# encoding: utf-8

import logging
from altair.app.ticketing.famiport.models import (
    FamiPortReceiptType,
    FamiPortOrderType,
)
from . import AES_SECRET_KEY
from Crypto.Cipher import AES
from Crypto import Random

logger = logging.getLogger(__name__)

def validate_rebook_cond(receipt, now):
    errors = []
    if receipt.canceled_at:
        logger.info('cancelled receipt is not rebookable')
        errors.append(u'当予約はキャンセル済みです')
    if not receipt.payment_request_received_at:
        logger.info('non paid/issued receipt is not rebookable')

    # FmiPortOrderTypeで対象receiptの入金期限/発券期限を確認する。
    if receipt.famiport_order.type == FamiPortOrderType.CashOnDelivery or FamiPortOrderType.PaymentOnly:
        if receipt.famiport_order.payment_due_at < now:
            logger.info('cannot rebook after payment due date is passed')
            errors.append(u'当予約は支払期日が過ぎているため同席番再予約できません')
    elif receipt.famiport_order.type == FamiPortOrderType.Payment:
        if receipt.type == FamiPortReceiptType.Payment.value and receipt.famiport_order.payment_due_at < now:
            logger.info('cannot rebook after payment due date is passed')
            errors.append(u'当予約は支払期日が過ぎているため同席番再予約できません')
        elif receipt.type == FamiPortReceiptType.Ticketing.value and receipt.famiport_order.ticketing_end_at < now:
            logger.info('cannot rebook after payment due date is passed')
            errors.append(u'当予約は発券期日が過ぎているため同席番再予約できません')
    elif receipt.famiport_order.type == FamiPortOrderType.Ticketing:
        if receipt.famiport_order.ticketing_end_at < now:
            logger.info('cannot rebook after payment due date is passed')
            errors.append(u'当予約は発券期日が過ぎているため同席番再予約できません')
    else:
        # ここに入ることはないはずです。
        logger.info('unknown famiport order type')
        errors.append(u'当予約のタイプが不正のため同席再予約できません')

    return errors

def validate_reprint_cond(receipt, now):
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
    def _is_token_expried(cls, created_at_str):
        from datetime import datetime, timedelta
        created_at = datetime.strptime(created_at_str, "%Y%m%d%H%M")
        now = datetime.now()
        # 発行したパスワードを変更するURLの有効期限は3時間
        return now > created_at + timedelta(hours=3)

    def _build_encrypting_str(self, text):
        # AESの暗号化が16 byteの文字列しか暗号化できないため、長さが16の文字列にする。
        return ''.join(['0'] * (16 - len(text))) + text

    @classmethod
    def get_cipher(cls, iv=None):
        if not iv:
            iv = Random.new().read(AES.block_size)
        cipher = AES.new(AES_SECRET_KEY, AES.MODE_CFB, iv)
        return cipher, iv

    @classmethod
    def get_id_from_token(cls, token):
    # tokenを復号して、ユーザID情報を返す。
        try:
            token = token.decode('hex')
            # 暗号化の副キーを取得
            iv = token[:16]
            # 暗号化したユーザID
            encrypted_user_id = token[16:32]
            # 暗号化した作成時間
            encrypted_created_at = token[32:]

            # 復号化
            cipher, _ = cls.get_cipher(iv)
            user_id_str = cipher.decrypt(encrypted_user_id)
            created_at_str = cipher.decrypt(encrypted_created_at)[4:]

            if not cls._is_token_expried(created_at_str):
                return int(user_id_str)
            else:
                return None
        except (ValueError, TypeError):
            return None

    # ユーザIDとトークンの作成時間を使って暗号化する。
    def get_token(self, user_id):
        if not user_id:
            return None

        from datetime import datetime
        created_at_str = datetime.now().strftime("%Y%m%d%H%M")

        # 文字列を16byteにする
        user_id_str = self._build_encrypting_str(str(user_id))
        created_at_str = self._build_encrypting_str(created_at_str)

        # 暗号化
        cipher, iv = self.get_cipher()
        encrypted_user_id = cipher.encrypt(user_id_str)
        encrypted_created_at = cipher.encrypt(created_at_str)

        # トークンを作成
        token = iv + encrypted_user_id + encrypted_created_at
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
    mailer.send(sender, recipient)
