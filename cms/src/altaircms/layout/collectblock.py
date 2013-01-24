from mako.lexer import Lexer
from mako.parsetree import BlockTag

def collect_block_name_from_makotemplate(text):
    nodes = _collect_block_node_from_makotemplate(text)
    return [n.name for n in nodes]

def _collect_block_node_from_makotemplate(text):
    r = []
    def _traverse(node):
        if hasattr(node, "nodes"):
            for n in node.nodes:
                _traverse(n)
        if isinstance(node, BlockTag):
            r.append(node)
    _traverse(Lexer(text, input_encoding="utf-8").parse())
    return r
