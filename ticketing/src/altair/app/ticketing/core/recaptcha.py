# coding=utf-8
import hashlib
import hmac
import re


class RecaptchaAuthorization(object):
    def __init__(self, api_key, api_secret):
        self.api_key = api_key
        self.api_secret = api_secret

    def generate_header_value(self):
        if self.api_key is None:
            return None

        hasher = hmac.new(self.api_key, self.api_secret, digestmod=hashlib.sha256)
        return hasher.hexdigest()

    def validate(self, val):
        return val == self.generate_header_value()


def recaptcha_exempt(request):
    """reCAPTCHAをスキップするリクエストかどうか判定する"""
    # Authorization Headerの値は
    # 固定の文字 (prefix) + space + ハッシュ値
    authorization = request.headers.get('Authorization', '')
    m = re.match(r'^([^\s]+)\s([^\s]+)$', authorization)
    if not m:
        return False

    prefix, hash_val = m.group(1), m.group(2)
    settings = request.registry.settings

    # Authorization値のprefixに一致する設定値を探す
    target = None
    for t in settings.get('recaptcha.exempt.targets', '').split(','):
        if prefix == settings.get('recaptcha.exempt.{}.prefix'.format(t)):
            target = t
            break

    if not target:
        return False

    api_key = settings.get('recaptcha.exempt.{}.auth_key'.format(target))
    api_secret = settings.get('recaptcha.exempt.{}.auth_secret'.format(target))

    if not api_key:
        return False

    # Authorization値をバリデーション
    header_authorization = RecaptchaAuthorization(api_key, api_secret)
    return header_authorization.validate(hash_val)
