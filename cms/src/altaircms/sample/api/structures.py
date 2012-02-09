from collections import defaultdict

"""
sorting data via orderno, easily.
"""

class NoPushBack(object):
    def __init__(self, zero=None, values=None):
        self.zero = zero
        self.xs = values or []

    def orderno(self, e):
        for i, x in enumerate(self._cleaned(self.xs)):
            if x == e:
                return i

    def append(self, e):
        self.xs.append(e)

    def delete(self, e):
        for i, x in enumerate(self.xs):
            if x == e:
                self.xs[i] = self.zero
                return True
        return False     # raise exception?
    
    def _orderno_to_index(self, orderno):
        for i, x in enumerate(self.xs):
            if x is not self.zero:
                if orderno == 0:
                    return i
                orderno -= 1
            
    def update_by_orderno(self, orderno, data):
        i = self._orderno_to_index(orderno)
        self.xs[i] = data
        
    def get_by_orderno(self, orderno):
        for i, x in enumerate(self._cleaned(self.xs)):
            if i == orderno:
                return x

    def __iter__(self):
        return self._cleaned(self.xs)

    def _cleaned(self, xs):
        return (x for x in xs if not x is self.zero)

    def __getstate__(self):
        return dict(zero=self.zero, xs=list(self._cleaned(self.xs)))

    def __eq__(self, other): #not good for performance
        return self.zero == other.zero and \
            list(self._cleaned(self.xs)) == list(self._cleaned(other.xs))
    
    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return str(self.xs)


class OrderedBlocks(object):
    @classmethod
    def from_dict(cls, D, zero=None):
        instance = cls()
        for k, vs in D.items():
            if hasattr(vs, "__iter__"):
                for v in vs:
                    instance.add(k, v)
            else:
                instance[k] = vs
        return instance

    def as_dict(self):
        D = {}
        for k, vs in self.blocks.items():
            D[k] =  list(vs._cleaned(vs.xs))
        return D

    def __init__(self):
        self.blocks = defaultdict(NoPushBack)
    
    def add(self, src, e):
        self.blocks[src].append(e)

    def delete(self, dst, e):
        self.blocks[dst].delete(e)

    def move(self, src, dst, e):
        self.add(dst, e)
        self.delete(src, e)

    def update_by_orderno(self, blockname, orderno, e):
        self.blocks[blockname].update_by_orderno(orderno, e)

    def orderno(self, blockname, e):
        return self.blocks[blockname].orderno(e)

    def __getitem__(self, src):
        return self.blocks[src]

    def __eq__(self, other):
        return self.blocks == other.blocks

    def __repr__(self):
        return str(self.blocks)

    def iteritems(self):
        return self.blocks.iteritems()

    __setitem__ = add

if __name__ == "__main__":
    import unittest 
    
    class NoPushBackTests(unittest.TestCase):
        def test_append(self):
            xs = NoPushBack(values=[1, 2, 3])
            xs.append(4)
            self.assertEquals(xs.xs, [1, 2, 3, 4])

        def test_delete1(self):
            xs = NoPushBack(values=[1, 2, 3])
            xs.delete(2)
            self.assertEquals(xs.xs, [1, None, 3])

        def test_delete_and_append(self):
            xs = NoPushBack(values=[1, 2, 3])
            xs.delete(2)
            xs.append(2)
            self.assertEquals(xs.xs, [1, None, 3, 2])

        def test_pickel_simple(self):
            import pickle
            xs = NoPushBack(values=[1, 2, 3])
            new_xs = pickle.loads(pickle.dumps(xs))
            self.assertEquals(new_xs.xs, [1, 2, 3])

        def test_pickel_zerovalue(self):
            import pickle
            xs = NoPushBack(values=[1, 2, 3], zero=-1)
            new_xs = pickle.loads(pickle.dumps(xs))
            self.assertEquals(new_xs.zero, xs.zero)

        def test_pickel2(self):
            import pickle
            xs = NoPushBack(values=[1, 2, 3])
            xs.delete(2)
            xs.append(2)

            new_xs = pickle.loads(pickle.dumps(xs))
            self.assertEquals(new_xs.xs, [1, 3, 2])

        def test_update_by_orderno_first(self):
            vals = [0, 1, 2, 3]
            xs = NoPushBack(values=vals, zero=0)
            xs.update_by_orderno(0, 100)
            self.assertEquals(xs.xs, [0, 100, 2, 3])

        def test_update_by_orderno(self):
            vals = [1, 0, 0, 2, 0, 0, 3]
            xs = NoPushBack(values=vals, zero=0)
            xs.update_by_orderno(2, 100)
            self.assertEquals(xs.xs, [1, 0, 0, 2, 0, 0, 100])

    class OrderedBlocksTests(unittest.TestCase):
        def test_from_dict(self):
            blocks0 = OrderedBlocks.from_dict(dict(x=[10], y=[20]))
            blocks1 = OrderedBlocks()
            blocks1["x"] = 10
            blocks1["y"] = 20
            self.assertEquals(blocks0, blocks1)

        def test_as_dict(self):
            blocks0 = OrderedBlocks.from_dict(dict(x=[10], y=[20]))
            self.assertEquals(blocks0.as_dict(), {'y': [20], 'x': [10]})

        def test_simple(self):
            blocks = OrderedBlocks()
            blocks.add("abc", 1)
            blocks.add("xyz", 10)
            blocks.add("abc", 2)

            self.assertEquals(blocks.orderno("abc", 1), 0)
            self.assertEquals(blocks.orderno("abc", 2), 1)
            self.assertEquals(blocks.orderno("xyz", 10), 0)

        def test_moveit(self):
            blocks = OrderedBlocks()
            blocks.add("abc", 1)
            blocks.add("xyz", 10)
            blocks.add("abc", 2)
            blocks.move("abc", "owo", 1)

            self.assertEquals(blocks.orderno("abc", 2), 0)
            self.assertEquals(blocks.orderno("xyz", 10), 0)
            self.assertEquals(blocks.orderno("owo", 1), 0)
            
        def test_moveit_pickle(self):
            blocks = OrderedBlocks()
            blocks.add("abc", 1)
            blocks.add("xyz", 10)
            blocks.add("abc", 2)
            blocks.move("abc", "owo", 1)

            import pickle
            new_blocks = pickle.loads(pickle.dumps(blocks))

            self.assertEquals(new_blocks["abc"], blocks["abc"])
            self.assertEquals(new_blocks["xyz"], blocks["xyz"])
            self.assertEquals(new_blocks["owo"], blocks["owo"])

    unittest.main()
