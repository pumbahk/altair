# encoding: utf-8
class Helpers(object):
    def __init__(self, request):
        self.request = request

    def auth_identifier_field_name(self, member_set):
        value = member_set.auth_identifier_field_name
        if value:
            return value
        else:
            return self.request.translate(u'ログイン名')

    def auth_secret_field_name(self, member_set):
        value = member_set.auth_secret_field_name
        if value:
            return value
        else:
            return self.request.translate(u'パスワード')
