# -*- coding: utf-8 -*-

class Session(object):
    def __init__(self, request):
        self.request = request
        self.session = request.session

    def put_session(self, key, value):
        self.session[key] = value

    def pop_session(self, key):
        ret = self.get_session(key)
        self.delete_session(key)
        return ret

    def exist_session(self, key):
        if key in self.session:
            return True
        return False

    def get_session(self, key):
        return self.session[key]

    def delete_session(self, key):
        del self.session[key]


class InquirySession(Session):

    def put_inquiry_session(self):
        self.put_session("inquiry", "inquiry")

    def exist_inquiry_session(self):
        return self.exist_session("inquiry")

    def get_inquiry_session(self):
        return self.get_session("inquiry")

    def delete_inquiry_session(self):
        self.delete_session("inquiry")
