#-*- coding: utf-8 -*-
import unittest
from unittest import TestCase
from .. import string as vh_string

import string


class RawTextTests(TestCase):
    def test_it(self):
        txt = string.printable
        rt = vh_string.RawText(txt)
        self.assertEqual(rt.value, txt)


class TruncateTest(TestCase):
    PRINTABLE_NO_WHITESPACE = string.ascii_letters\
        + string.digits + string.punctuation

    def test_ascii_code(self):
        msg = self.PRINTABLE_NO_WHITESPACE
        ll = len(msg)
        _ = vh_string.truncate

        # default ellipse
        el = '...'
        self.assertEqual(_(msg, size=ll+1), msg)
        self.assertEqual(_(msg, size=ll+0), msg)
        self.assertEqual(_(msg, size=ll-1), msg[:ll-1]+el)
        self.assertEqual(_(msg, size=ll-2), msg[:ll-2]+el)

        # customize ellipse
        el = u'日本語'
        self.assertEqual(_(msg, size=ll+1, ellipsis=el), msg)
        self.assertEqual(_(msg, size=ll+0, ellipsis=el), msg)
        self.assertEqual(_(msg, size=ll-1, ellipsis=el), msg[:ll-1]+el)
        self.assertEqual(_(msg, size=ll-2, ellipsis=el), msg[:ll-2]+el)


class EastAsianTruncateTest(TruncateTest):
    GANA = u'ひらがな'
    KANA = u'カタカナ'
    KANJI = u'日本語漢字'
    SYMBOL = u'：１２３４５６７８９０ー＾￥＠「；：」、。・＿｀『＋＊』＜＞？＿'
    KANA_HARF = u'ﾊﾝｶｸｶﾀｶﾅ'

    def test_full_width(self):
        """The full-width size character test.

        1 full-width char == 2 width.
        """
        _ = vh_string.truncate_eaw
        for msg in (self.GANA, self.KANA, self.SYMBOL, self.KANJI):
            ll = len(msg)
            llx2 = ll * 2

            # default ellipse
            el = '...'
            self.assertEqual(_(msg, width=llx2+1), msg)
            self.assertEqual(_(msg, width=llx2+0), msg)
            self.assertEqual(_(msg, width=llx2-1), msg[:ll-1]+el)
            self.assertEqual(_(msg, width=llx2-2), msg[:ll-1]+el)
            self.assertEqual(_(msg, width=llx2-3), msg[:ll-2]+el)
            self.assertEqual(_(msg, width=llx2-4), msg[:ll-2]+el)

            # customize ellipse
            el = u'日本語'
            self.assertEqual(_(msg, width=llx2+1, ellipsis=el), msg)
            self.assertEqual(_(msg, width=llx2+0, ellipsis=el), msg)
            self.assertEqual(_(msg, width=llx2-1, ellipsis=el), msg[:ll-1]+el)
            self.assertEqual(_(msg, width=llx2-2, ellipsis=el), msg[:ll-1]+el)
            self.assertEqual(_(msg, width=llx2-3, ellipsis=el), msg[:ll-2]+el)
            self.assertEqual(_(msg, width=llx2-4, ellipsis=el), msg[:ll-2]+el)

    def test_harf_width(self):
        _ = vh_string.truncate_eaw
        # all harf-width japanese
        msg = self.KANA_HARF
        ll = len(msg)

        # default ellipse
        el = '...'
        self.assertEqual(_(msg, width=ll+1), msg)
        self.assertEqual(_(msg, width=ll+0), msg)
        self.assertEqual(_(msg, width=ll-1), msg[:ll-1]+el)
        self.assertEqual(_(msg, width=ll-2), msg[:ll-2]+el)

        # customize ellipse
        el = u'日本語'
        self.assertEqual(_(msg, width=ll+1, ellipsis=el), msg)
        self.assertEqual(_(msg, width=ll+0, ellipsis=el), msg)
        self.assertEqual(_(msg, width=ll-1, ellipsis=el), msg[:ll-1]+el)
        self.assertEqual(_(msg, width=ll-2, ellipsis=el), msg[:ll-2]+el)


class ConvertEOLTest(TestCase):
    def runTest(self):
        res = vh_string.nl_to_br('test\n')
        self.assertEqual(res.value, 'test<br/>')
