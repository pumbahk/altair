# -*- coding:utf-8 -*-

from altaircms.security import RootFactory

class AssetResource(RootFactory):
    def __init__(self, request):
        super(RootFactory, self).__init__()
