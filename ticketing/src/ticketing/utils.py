# -*- coding:utf-8 -*-
from standardenum import StandardEnum

class DigitCodec(object):
    def __init__(self, digits):
        self.digits = digits

    def encode(self, num):
        l = len(self.digits)
        retval = []
        n = num
        while True:
            rem = n % l
            quo = n // l
            retval.insert(0, self.digits[rem])
            if quo == 0:
                break
            n = quo
        return ''.join(retval)

    def decode(self, s):
        i = 0
        sl = len(s)
        l = len(self.digits)
        retval = 0
        while i < sl:
            c = s[i]
            d = self.digits.find(c)
            if d < 0:
                raise ValueError("Invalid digit: " + c)
            retval *= l
            retval += d
            i += 1
        return retval

encoder = DigitCodec("0123456789ACFGHJKLPRSUWXYZ")
sensible_alnum_encode = encoder.encode
sensible_alnum_decode = encoder.decode
