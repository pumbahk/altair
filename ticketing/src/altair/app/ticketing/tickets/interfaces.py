# -*- coding:utf-8 -*-
from zope.interface import Interface

class ISVGBuilder(Interface):
    def build(template, vals):
        pass
