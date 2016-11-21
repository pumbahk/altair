#! /usr/bin/env python
# -*- coding: utf-8 -*-
from altair.sqlahelper import get_db_session
from altair.app.ticketing.core.models import Performance


class PerformanceCodeGenerator(object):
    # A-Z
    CHR_MIN = 65
    CHR_MAX = 91

    def __init__(self, request, max_digit=12):
        self._slave_session = get_db_session(request, name="slave")
        self._max_digit = max_digit
        self._used_chr_code = []

    # 指定されたリストにないコードを見つける
    def generate_code(self, code):
        change_digit = ""
        digit = 0
        while digit <= self._max_digit:
            for _ in reversed(range(self.CHR_MIN, self.CHR_MAX)):
                for chr_code in reversed(range(self.CHR_MIN, self.CHR_MAX)):
                    chr_code_str = chr(chr_code)

                    # コードの形にする
                    part = "{0}{1}".format(change_digit, chr_code_str)
                    generate_code = "{0}{1}".format(code[:-len(part)], part)

                    if generate_code not in self._used_chr_code:
                        return generate_code

                # 左の桁を、ZからAまで下げていく
                if len(change_digit) > 0:
                    one_digit = chr(ord(change_digit[:1]) - 1)
                    change_digit = one_digit + change_digit[1:12]

            change_digit = ""
            for _ in range(digit):
                change_digit += "Z"

            digit += 1
        return None

    # 払い出したコードが、DBになければ新規コード
    def generate(self, code):
        while self.generate_code(code):
            generated_code = self.generate_code(code)
            self._used_chr_code.append(generated_code)

            performance = self._slave_session.query(Performance).\
                filter(Performance.code == generated_code).first()

            if not performance:
                return generated_code
