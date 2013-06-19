# -*- coding:utf-8 -*-
from .api import create_or_update_mailinfo,  create_fake_order

def get_mailtype_description():
    return u"抽選メール"

def get_subject_info_default():
    return LotsInfoDefault

class LotsInfoDefault(object):
    pass

class LotsMail(object):
    pass
