# encoding: utf-8

class InvalidPage(Exception):
    pass

class PageNotInInteger(InvalidPage):
    pass

class EmptyPage(InvalidPage):
    pass