import itertools
from . import emitters
from . import core
from . import eval as eval_

def compile_predicate_to_ast(expr):
    return core.Parser(core.Tokenizer(expr))()

def compile_predicate_to_pycode(expr):
    if isinstance(expr, core.Node):
        ast = expr
    else:
        ast = compile_predicate_to_ast(expr)
    emit = emitters.PythonCodeEmitter()
    emitters.GenericCodeEmittingVisitor(emit, emitters.generic_boolean_op_func_handler)(ast)
    return compile(u''.join(emit.buf), 'eval', 'eval')

def eval_compiled_predicate(code, var_resolver, sym_resolver, comparator_factory=None, caster=None):
    if comparator_factory is None:
        comparator_factory = eval_.Comparator
    if caster is None:
        caster = eval_.Caster()
    comparator = comparator_factory(caster)
    ctx = dict(
        to_float=caster.to_float,
        to_string=caster.to_string,
        equal=comparator.equal,
        greater=comparator.greater,
        var=var_resolver,
        sym=sym_resolver
        )
    return eval(code, None, ctx)


def _iterate_breadth_first(n):
    return itertools.chain(
        n.children,
        itertools.chain.from_iterable(_iterate_breadth_first(cn) for cn in n.children)
        )

def iterate_breadth_first(n):
    return itertools.chain((n, ), _iterate_breadth_first(n))

def iterate_depth_first(n):
    return itertools.chain(
        (n, ),
        itertools.chain.from_iterable(iterate_depth_first(cn) for cn in n.children)
        )

def iterate_variables(n):
    return [cn.value for cn in iterate_depth_first(n) if cn.type == 'VAR']
