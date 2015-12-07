# encoding: utf-8
class Helpers(object):
    def __init__(self, request):
        self.request = request

    def auth_identifier_field_name(self, member_set):
        value = member_set.auth_identifier_field_name
        if value is not None:
            return value
        else:
            return u'ログイン名'

    def auth_secret_field_name(self, member_set):
        value = member_set.auth_secret_field_name
        if value is not None:
            return value
        else:
            return u'パスワード'
