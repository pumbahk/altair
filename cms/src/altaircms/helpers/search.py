# -*- coding:utf-8 -*-


def escape_wildcard_for_like(string):
    if string is None:
        return string
    else:
        string = string.replace('%', '\%')
        string = string.replace('_', '\_')
        return string
