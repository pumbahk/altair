# encoding: utf-8

from Crypto.Cipher import AES
from Crypto import Random

from altair.app.ticketing.ssl_utils import get_certificate_info

from . import AES_SECRET_KEY

import logging
logger = logging.getLogger(__name__)

def get_auth_identifier_from_client_certified_request(request):
    subject_dn, serial = get_certificate_info(request)
    logger.info("[get_auth_identifier_from_client_certified_request] subject_dn = {subject_dn}, serial = {serial}"
                .format(subject_dn=subject_dn, serial=serial))
    if subject_dn is not None:
        return '%s:%s' % (subject_dn, serial)
    return None

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