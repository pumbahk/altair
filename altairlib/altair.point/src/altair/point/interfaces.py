# -*- coding:utf-8 -*-
from zope.interface import Interface, Attribute


class IPointAPICommunicator(Interface):
    """
    ポイントAPIと通信を行うクライアントクラスです。
    以下の4種類のAPIへのリクエストを行います。
    get-stdonly
    auth-stdonly
    fix
    rollback
    """
    def request_get_stdonly(self, easy_id):
        pass

    def request_auth_stdonly(self, easy_id, auth_point, req_time):
        pass

    def request_fix(self, easy_id, fix_point, unique_id, fix_id, req_time):
        pass

    def request_rollback(self, easy_id, unique_id):
        pass


class IPointAPICommunicatorFactory(Interface):
    """
    ポイントAPIクライアントを呼び出すためのFactoryクラスです。 　
    """
    def __call__(self):
        pass
