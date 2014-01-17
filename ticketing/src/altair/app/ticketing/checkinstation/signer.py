# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import hashlib

class Signer(object):
    salt = ":hihihi"
    def __init__(self, secret):
        self.secret = secret

    def sign(self):
        return hashlib.sha1(self.secret+self.salt).hexdigest()

    def verify(self, signed):
        return signed == self.sign()


def verify_secret_token_decorator_factory(get_secret):
    def with_secret_token(context, request):
        """validation後のPOSTはsecret tokenを持つ"""
        try:
            identity = context.identity
        except Exception:
            logger.warn("verify failure identity not found")
            return False

        try:
            internal_secret = identity.secret
            signer = Signer(internal_secret)
            secret_token = get_secret(request) 
            if not signer.verify(secret_token):
                logger.warn("verify failure. secret_token=%s", secret_token)
                return False
            return True
        except Exception:
            logger.exception("verify failure. (identity.id=%s)", identity)
            return False;
    return with_secret_token

def get_secret_from_json_body(request):
    try:
        return request.json_body["secret"]
    except KeyError:
        logger.warn("KeyError: request.json_body['secret']")
        return ""

with_secret_token = verify_secret_token_decorator_factory(get_secret_from_json_body)
