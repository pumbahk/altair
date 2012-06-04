from . import renderable
import unittest

class RenderableTest(unittest.TestCase):
    def test_obi_empty(self):
        return renderable.obi(None, [], None)

    # @mock.patch("")
    # def test_obi(self):
    #     return renderable.obi(None, demo.dummy_performances, None)

    # def test_tab_empty(self):
    #     return renderable.tab(None, [], None)


    # def test_tab(self):
    #     pass

if __name__ == "__main__":
    unittest.main()
