import unittest

class TestEval(unittest.TestCase):
    def test_basic(self):
        from .utils import compile_predicate_to_pycode, eval_compiled_predicate
        v = eval_compiled_predicate(
            compile_predicate_to_pycode(u'{var} + {var} * 2'),
            var_resolver=dict(var=1).__getitem__,
            sym_resolver=dict(func=lambda x: x)
            )
        self.assertEqual(v, 3)

    def test_func(self):
        from .utils import compile_predicate_to_pycode, eval_compiled_predicate
        v = eval_compiled_predicate(
            compile_predicate_to_pycode(u'func({var} + {var} * 2)'),
            var_resolver=dict(var=1).__getitem__,
            sym_resolver=dict(func=lambda x: x * 2).__getitem__
            )
        self.assertEqual(v, 6)

    def test_special_func(self):
        from .utils import compile_predicate_to_pycode, eval_compiled_predicate
        v = eval_compiled_predicate(
            compile_predicate_to_pycode(u'AND(AND({var}, 1), OR(0, 0))'),
            var_resolver=dict(var=1).__getitem__,
            sym_resolver=dict().__getitem__
            )
        self.assertEqual(v, 0)


class TestIterateBreadthFirst(unittest.TestCase):
    def test_basic(self):
        from .core import Node
        n = Node(
            type='A',
            children=[
                Node(type='B'),
                Node(
                    type='C',
                    children=[
                        Node(type='E'),
                        Node(
                            type='F',
                            children=[
                                Node(type='H')
                                ]
                            ),
                        Node(type='G'),
                        ]
                    ),
                Node(type='D'),
                ]
            )
        from .utils import iterate_breadth_first
        self.assertEqual(
            [cn.type for cn in iterate_breadth_first(n)],
            ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
            )


class TestIterateDepthFirst(unittest.TestCase):
    def test_basic(self):
        from .core import Node
        n = Node(
            type='A',
            children=[
                Node(type='B'),
                Node(
                    type='C',
                    children=[
                        Node(type='E'),
                        Node(
                            type='F',
                            children=[
                                Node(type='H')
                                ]
                            ),
                        Node(type='G'),
                        ]
                    ),
                Node(type='D'),
                ]
            )
        from .utils import iterate_depth_first
        self.assertEqual(
            [cn.type for cn in iterate_depth_first(n)],
            ['A', 'B', 'C', 'E', 'F', 'H', 'G', 'D']
            )

