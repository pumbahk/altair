# coding: utf-8

import unittest
from altaircms.models import Category, Word
from altaircms.page.models import PageSet
from datetime import datetime


def setUpModule():
    pass


class WordTests(unittest.TestCase):
    def test_build_word_merge(self):
        from .word import build_word_merge

        w1_2 = Word()
        w1_2.id = 1
        w1_2.label = "らべる"
        setattr(w1_2, "_merge_word_id", 2)

        w1_3 = Word()
        w1_3.id = 1
        w1_3.label = "らべる"
        setattr(w1_3, "_merge_word_id", 3)

        w4 = Word()
        w4.id = 4
        w4.label = "たんご"
        setattr(w4, "_merge_word_id", None)
        setattr(w4, "_dummy_attr", "dummy")

        built = build_word_merge([w1_2, w1_3, w4, w4])
        expected = [
            {"id": 1, "label": "らべる", "merge": [2, 3]},
            {"id": 4, "label": "たんご", "merge": []},
        ]
        self.assertEquals(sorted(built, key=lambda x: x['id']),
                          sorted(expected, key=lambda x: x['id']))


if __name__ == "__main__":
    unittest.main()
