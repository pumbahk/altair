# coding: utf-8
from exceptions import Exception

class AuthenticationError(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg