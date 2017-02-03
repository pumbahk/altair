# -*- coding:utf-8 -*-

import unittest
import mock

class CreateOauthSignatureTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import oauth
        return oauth.create_oauth_signature(*args, **kwargs)

    def __get_base_args(self):
        return dict(
            oauth_consumer_key="dpf43f3p2l4k3l03",
            oauth_token="nnch734d00sl2jdk",
            oauth_signature_method="HMAC-SHA1",
            oauth_timestamp="1191242096",
            oauth_nonce="kllo9940pd9333jh",
            secret='kd94hf93k423kf44&pfkkdhi9sl3r4s00',
            method="GET",
            url="http://photos.example.net/photos"
        )

    def test_it(self):
        args = self.__get_base_args()
        result = self._callFUT(
            method=args['method'],
            url=args['url'],
            oauth_consumer_key=args['oauth_consumer_key'],
            secret=args['secret'],
            oauth_token=args['oauth_token'],
            oauth_signature_method=args['oauth_signature_method'],
            oauth_timestamp=args['oauth_timestamp'],
            oauth_nonce=args['oauth_nonce'])

        self.assertEqual(result, "0KnD/Q2NLb/Vu3gPoQIuNofV5AE=")

class CreateSignatureBaseTests(unittest.TestCase):
    def _callFUT(self, *args, **kwargs):
        from . import oauth
        return oauth.create_signature_base(*args, **kwargs)

    def __get_base_args(self):
        return dict(
            oauth_consumer_key="dpf43f3p2l4k3l03",
            oauth_token="nnch734d00sl2jdk",
            oauth_signature_method="HMAC-SHA1",
            oauth_timestamp="1191242096",
            oauth_nonce="kllo9940pd9333jh",
            secret='kd94hf93k423kf44&pfkkdhi9sl3r4s00',
            method="GET",
            url="http://photos.example.net/photos"
        )

    def request_token_base_test(self):
        """ リクエストトークン取得時のベース """
        args = self.__get_base_args()
        args['oauth_callback'] = "http://callback.com/here"
        result = self._callFUT(
            method=args['method'],
            url=args['url'],
            oauth_consumer_key=args['oauth_consumer_key'],
            oauth_token='',
            oauth_signature_method=args['oauth_signature_method'],
            oauth_timestamp=args['oauth_timestamp'],
            oauth_nonce=args['oauth_nonce'],
            oauth_callback=args['oauth_callback'],
            oauth_verifier='')

        self.assertEqual(result, 'GET&http%3A%2F%2Fphotos.example.net%2Fphotos&oauth_callback%3Dhttp%253A%252F%252Fcallback.com%252Fhere%26oauth_consumer_key%3Ddpf43f3p2l4k3l03%26oauth_nonce%3Dkllo9940pd9333jh%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1191242096')

    def access_token_base_test(self):
        """ アクセストークン取得時のベース """
        args = self.__get_base_args()
        args['oauth_token'] = "request_token"
        args['oauth_verifier'] = "oauth_verifier"
        result = self._callFUT(
            method=args['method'],
            url=args['url'],
            oauth_consumer_key=args['oauth_consumer_key'],
            oauth_token=args['oauth_token'],
            oauth_signature_method=args['oauth_signature_method'],
            oauth_timestamp=args['oauth_timestamp'],
            oauth_nonce=args['oauth_nonce'],
            oauth_callback='',
            oauth_verifier=args['oauth_verifier'])

        self.assertEqual(result, 'GET&http%3A%2F%2Fphotos.example.net%2Fphotos&oauth_consumer_key%3Ddpf43f3p2l4k3l03%26oauth_nonce%3Dkllo9940pd9333jh%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1191242096%26oauth_token%3Drequest_token%26oauth_verifier%3Doauth_verifier')

    def resouce_api_base_test(self):
        """ リソースAPIからデータ取得時のベース """
        args = self.__get_base_args()
        args['oauth_token'] = "access_token"
        result = self._callFUT(
            method=args['method'],
            url=args['url'],
            oauth_consumer_key=args['oauth_consumer_key'],
            oauth_token=args['oauth_token'],
            oauth_signature_method=args['oauth_signature_method'],
            oauth_timestamp=args['oauth_timestamp'],
            oauth_nonce=args['oauth_nonce'],
            oauth_callback='',
            oauth_verifier='')

        self.assertEqual(result, 'GET&http%3A%2F%2Fphotos.example.net%2Fphotos&oauth_consumer_key%3Ddpf43f3p2l4k3l03%26oauth_nonce%3Dkllo9940pd9333jh%26oauth_signature_method%3DHMAC-SHA1%26oauth_timestamp%3D1191242096%26oauth_token%3Daccess_token')
