from altaircms.page.models import HasAncestorMixin
import unittest

class Node(HasAncestorMixin):
    def __init__(self, v, parent=None):
        self.parent = parent
        self.v = v

class HasAncestorMixinTest(unittest.TestCase):
    def test_self(self):
        self.assertEquals([n.v for n in Node(10).ancestors], 
                         [])

    def test_parent_and_child(self):
        parent = Node(10)
        child = Node(20, parent=parent)
        self.assertEquals([n.v for n in child.ancestors], 
                         [10])

if __name__ == "__main__":
    unittest.main()
