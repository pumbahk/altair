# -*- coding:utf-8 -*-
import itertools
from .redirect import Failure
from .api import get_preview_secret

class PermissionDataNotFound(Exception):
    pass

def load_preview_permission(request):
    session = request.session
    data_type = session.get("type")
    if data_type == "operator":
        return OperatorPermissionData.load(request)
    elif data_type == "accesskey":
        return AccesskeyPermissionData.load(request)
    else:
        raise PermissionDataNotFound(data_type)

class PreviewPermissionData(dict):
    permission = ("expire_at", "backend_event_id", "event_id", "scope")
    identify = ("type", "operator_id", "accesskey", "secret")

    @classmethod
    def fields(cls):
        return itertools.chain.from_iterable([cls.permission, cls.identify])

    def dump(self, request):
        session = request.session
        for k in self.fields():
            v = self.get(k)
            if v:
                session[k] = v
        return session

    def invalidate(self, request):
        session = request.session
        for k in self.fields():
            if k in session:
                del session[k]
        return session

    @classmethod
    def load(cls, request):
        session = request.session
        data = cls()
        for k in cls.fields():
            v = session.get(k)
            if v:
                data[k] = v
        return data

class OperatorPermissionData(PreviewPermissionData):
    permission = ("expire_at", )
    identify = ("type", "operator_id", "secret")

    @classmethod
    def is_this(cls, this):
        return this["type"] == "operator"

    @classmethod
    def create(cls, operator, secret=None):
        return cls(
            type="operator", 
            expire_at=operator.expire_at, 
            scope="all", 
            operator_id = operator.id, 
            secret=secret
            )


    def verify(self, request):
        key_string = self.get("operator_id")
        if key_string is None:
            return Failure(u"ログインユーザの認証キー文字列がセッションから取得できません")
        secret = self.get("secret")
        if secret is None:
            return Failure(u"不正な経路で値が設定されました")
        if get_preview_secret(request)(key_string) != secret:
            return Failure(u"ログインユーザの認証キーの検証に失敗しました")
        return True

class AccesskeyPermissionData(PreviewPermissionData):
    permission = ("expire_at", "backend_event_id", "event_id", "scope")
    identify = ("type", "accesskey", "secret")

    @classmethod
    def is_this(cls, this):
        return this["type"] == "accesskey"

    @classmethod
    def create_from_dict(cls, data, secret=None):
        return cls(
            type="accesskey", 
            expire_at=data["expiredate"], 
            backend_event_id=data["backend_event_id"], 
            event_id=data["event_id"], 
            scope=data["scope"], 
            accesskey=data["accesskey"], 
            secret=secret
            )

    def verify(self, request):
        key_string = self.get("accesskey")
        if key_string is None:
            return Failure(u"認証キー文字列がセッションから取得できません")
        secret = self.get("secret")
        if secret is None:
            return Failure(u"不正な経路で値が設定されました")
        if get_preview_secret(request)(key_string) != secret:
            return Failure(u"認証キーの検証に失敗しました")
        return True
