# -*- coding:utf-8 -*-

class LotCloser(object):
    def __init__(self, lot, request):
        self.request = request
        self.lot = lot


    def close(self):
        # オプションで、当選でもDeliveryMethod処理が終わっていないものもクローズする可能性がある
        for entry in self.lot.remained_entries:
            entry.close()


