# encoding: utf-8

from .models import SexEnum

def format_sex(request, gender):
    if SexEnum.NoAnswer.v == int(gender):
        return u'無回答'
    elif SexEnum.Male.v == int(gender):
        return u'男性'
    elif SexEnum.Female.v == int(gender):
        return u'女性'

