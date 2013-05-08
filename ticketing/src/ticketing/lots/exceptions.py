# -*- coding:utf-8 -*-

class NotElectedException(Exception):
    """ 当選していない抽選 """


class OutTermException(Exception):
    def __init__(self, lot_name, from_, to_):
        super(OutTermException, self).__init__()
        self.lot_name = lot_name
        self.from_ = from_
        self.to_ = to_
