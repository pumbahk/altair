from .core import DSLError, Visitor
import math

NaN = float('NaN')

class DSLRuntimeError(DSLError):
    pass 

class Caster(object):
    def __init__(self):
        pass

    def to_float(self, o):
        if not isinstance(o, float):
            try:
                return float(o)
            except (TypeError, ValueError):
                return NaN
        else:
            return o

    def to_string(self, o):
        if o is None:
            return u''
        elif isinstance(o, float):
            return u'%g' % o
        elif not isinstance(o, unicode):
            return unicode(o)
        else:
            return o


class Comparator(object):
    def __init__(self, caster):
        self.caster = caster

    def _cast(self, l, r):
        _l = self.caster.to_float(l)
        _r = self.caster.to_float(r)
        if not math.isnan(_l) and not math.isnan(_r):
            return _l, _r
        return self.caster.to_string(l), self.caster.to_string(r)

    def equal(self, l, r):
        l, r = self._cast(l, r)
        return l == r

    def greater(self, l, r):
        l, r = self._cast(l, r)
        return l > r


class Evaluator(Visitor):
    def __init__(self, sym_resolver, var_resolver, caster, comparator):
        self.sym_resolver = sym_resolver
        self.var_resolver = var_resolver
        self.caster = caster
        self.comparator = comparator

    def build_undefined_variable_error(self, n, ctx):
        return DSLRuntimeError('unable to resolve variable %s', n.value, line=n.line, column=n.column)

    def build_undefined_symbol_error(self, n, ctx):
        return DSLRuntimeError('unable to resolve symbol %s', n.value, line=n.line, column=n.column)

    def visit_NUM(self, n, ctx):
        return n.value

    def visit_STR(self, n, ctx):
        return n.value

    def visit_VAR(self, n, ctx):
        v = self.var_resolver(n.value)
        if v is None:
            raise self.build_undefined_variable_error(n, ctx)
        return v

    def visit_SYM(self, n, ctx):
        v = self.sym_resolver(n.value)
        if v is None:
            raise self.build_undefined_symbol_error(n, ctx)
        return v

    def visit_CALL(self, n, ctx):
        fn = self.visit(n.children[0], n)
        args = self.visit(n.children[1], n)
        return fn(*args)

    def visit_TUPLE(self, n, ctx):
        return [self.visit(arg, n) for arg in n.children]

    def visit_EQ(self, n, ctx):
        return self.comparator.equal(self.visit(n.children[0], n), self.visit(n.children[1], n))

    def visit_NE(self, n, ctx):
        return not self.comparator.equal(self.visit(n.children[0], n), self.visit(n.children[1], n))

    def visit_GT(self, n, ctx):
        return self.comparator.greater(self.visit(n.children[0], n), self.visit(n.children[1], n))

    def visit_LT(self, n, ctx):
        return self.comparator.greater(self.visit(n.children[1], n), self.visit(n.children[0], n))

    def visit_GE(self, n, ctx):
        return not self.comparator.greater(self.visit(n.children[1], n), self.visit(n.children[0], n))

    def visit_LE(self, n, ctx):
        return not self.comparator.greater(self.visit(n.children[0], n), self.visit(n.children[1], n))

    def visit_ADD(self, n, ctx):
        l = self.caster.to_float(self.visit(n.children[0], n))
        r = self.caster.to_float(self.visit(n.children[1], n))
        return l + r

    def visit_SUB(self, n, ctx):
        l = self.caster.to_float(self.visit(n.children[0], n))
        r = self.caster.to_float(self.visit(n.children[1], n))
        return l - r

    def visit_MUL(self, n, ctx):
        l = self.caster.to_float(self.visit(n.children[0], n))
        r = self.caster.to_float(self.visit(n.children[1], n))
        return l * r

    def visit_DIV(self, n, ctx):
        l = self.caster.to_float(self.visit(n.children[0], n))
        r = self.caster.to_float(self.visit(n.children[1], n))
        return l / r

    def visit_CON(self, n, ctx):
        l = self.caster.to_string(self.visit(n.children[0], n))
        r = self.caster.to_string(self.visit(n.children[1], n))
        return l + r

    def visit(self, n, ctx):
        return n.accept(self, ctx)

    def __call__(self, n):
        return self.visit(n, None)



