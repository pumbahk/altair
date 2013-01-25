import unittest
import os
here = os.path.abspath(os.path.dirname(__file__))


class helperTests(unittest.TestCase):
    def test_swf_width_height_compressed(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(os.path.join(here, "w480h445.compressed.swf")) as io:
            result = swf_width_and_height(io)

            self.assertEquals(result, (480, 445))

    def test_swf_width_height(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(os.path.join(here, "w480h445.swf")) as io:
            result = swf_width_and_height(io)

            self.assertEquals(result, (480, 445))


    def test_swf_width_height_invalid(self):
        from altaircms.asset.swfrect import swf_width_and_height
        with open(__file__) as io:
            self.assertRaises(Exception, lambda : swf_width_and_height(io))
