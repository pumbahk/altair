import re
from .core import ParseError, Visitor

class PythonCodeEmitter(object):
    escapes = {
        '\\': '\\',
        '"': '"',
        '\'': '\'',
        '\a': 'a',
        '\b': 'b',
        '\f': 'f',
        '\n': 'n',
        '\r': 'r',
        '\t': 't',
        '\v': 'v',
        }

    def __init__(self):
        self.buf = []
 
    def _escape(self, v):
        def fn(g):
            c = g.group(0)
            v = self.escapes.get(c)
            if v is None:
                return u'\\x%x' % ord(c)
            else:
                return u'\\%s' % v
        return re.sub(ur'[\x00-\x1f"\\\x7f]', fn, v)

    def emit_add(self):
        self.buf.append(u'+')

    def emit_div(self):
        self.buf.append(u'/')

    def emit_float(self, v):
        v = u'%g' % v
        if u'.' not in v:
            v += '.'
        self.buf.append(v)

    def emit_lparen(self):
        self.buf.append(u'(')

    def emit_mul(self):
        self.buf.append(u'*')

    def emit_rparen(self):
        self.buf.append(u')')

    def emit_string(self, v):
        self.buf.append(u'u"%s"' % self._escape(v))

    def emit_sub(self):
        self.buf.append(u'-')

    def emit_sym_reference(self, v):
        self.buf.append(u'sym(')
        self.emit_string(v)
        self.buf.append(u')')

    def emit_var_reference(self, v):
        self.buf.append(u'var(')
        self.emit_string(v)
        self.buf.append(u')')

    def emit_begin_string_cast(self):
        self.buf.append(u'to_string(')

    def emit_end_string_cast(self):
        self.buf.append(u')')

    def emit_begin_float_cast(self):
        self.buf.append(u'to_float(')

    def emit_end_float_cast(self):
        self.buf.append(u')')

    def emit_comma(self):
        self.buf.append(u',')

    def emit_begin_equal(self):
        self.buf.append(u'equal(')

    def emit_end_equal(self):
        self.buf.append(u')')

    def emit_begin_not_equal(self):
        self.buf.append(u'not equal(')

    def emit_end_not_equal(self):
        self.buf.append(u')')

    def emit_begin_greater(self):
        self.buf.append(u'greater(')

    def emit_end_greater(self):
        self.buf.append(u')')

    def emit_begin_less_or_equal(self):
        self.buf.append(u'not greater(')

    def emit_end_less_or_equal(self):
        self.buf.append(u')')

    def emit_and(self):
        self.buf.append(u' and ')

    def emit_or(self):
        self.buf.append(u' or ')

    def emit_not(self):
        self.buf.append(u'not ')


def generic_boolean_op_func_handler(n, ctx, visitor):
    assert n.children[0].type == 'SYM'
    op = n.children[0].value.lower()
    def enclose_if_not_leaf(visitor, n, ctx):
        if n.type in ('VAR', 'SYM', 'NUM', 'STR'):
            visitor.visit(n, ctx)
        else:
            visitor.emitter.emit_lparen()
            visitor.visit(n, ctx)
            visitor.emitter.emit_rparen()

    if op == 'and':
        if len(n.children[1].children) != 2:
            raise ParseError('wrong number of arguments for AND function')
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_and()
        enclose_if_not_leaf(visitor, n.children[1].children[1], n)
        visitor.emitter.emit_rparen()
        return True
    elif op == 'or':
        if len(n.children[1].children) != 2:
            raise ParseError('wrong number of arguments for OR function')
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_or()
        enclose_if_not_leaf(visitor, n.children[1].children[1], n)
        visitor.emitter.emit_rparen()
        return True
    elif op == 'not':
        if len(n.children[1].children) != 1:
            raise ParseError('wrong number of arguments for NOT function')
        visitor.emitter.emit_not()
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_rparen()
        return True


class GenericCodeEmittingVisitor(Visitor):
    associativities = {
        'EQ': 1,
        'NE': 1,
        'CON': 2,
        'ADD': 3,
        'SUB': 3,
        'MUL': 4,
        'DIV': 4,
        'STR': 10,
        'NUM': 10,
        'VAR': 10,
        'SYM': 10,
        }

    def __init__(self, emitter, func_handler=None):
        self.emitter = emitter
        self.func_handler = func_handler

    def visit_NUM(self, n, ctx):
        self.emitter.emit_float(n.value)

    def visit_STR(self, n, ctx):
        self.emitter.emit_string(n.value)

    def visit_VAR(self, n, ctx):
        self.emitter.emit_var_reference(n.value)

    def visit_SYM(self, n, ctx):
        self.emitter.emit_sym_reference(n.value)

    def visit_CALL(self, n, ctx):
        if self.func_handler is None or not self.func_handler(n, ctx, self):
            self.visit(n.children[0], n)
            self.visit(n.children[1], n)

    def visit_TUPLE(self, n, ctx):
        self.emitter.emit_lparen()
        for i, arg in enumerate(n.children):
            if i > 0:
                self.emitter.emit_comma()
            self.visit(arg, n)
        self.emitter.emit_rparen()

    def visit_EQ(self, n, ctx):
        self.emitter.emit_begin_equal()
        self.visit(n.children[0], n)
        self.emitter.emit_comma()
        self.visit(n.children[1], n)
        self.emitter.emit_end_equal()

    def visit_NE(self, n, ctx):
        self.emitter.emit_begin_not_equal()
        self.visit(n.children[0], n)
        self.emitter.emit_comma()
        self.visit(n.children[1], n)
        self.emitter.emit_end_equal()

    def visit_GT(self, n, ctx):
        self.emitter.emit_begin_greater()
        self.visit(n.children[0], n)
        self.emitter.emit_comma()
        self.visit(n.children[1], n)
        self.emitter.emit_end_greater()

    def visit_LT(self, n, ctx):
        self.emitter.emit_begin_greater()
        self.visit(n.children[1], n)
        self.emitter.emit_comma()
        self.visit(n.children[0], n)
        self.emitter.emit_end_greater()

    def visit_GE(self, n, ctx):
        self.emitter.emit_begin_less_or_equal()
        self.visit(n.children[1], n)
        self.emitter.emit_comma()
        self.visit(n.children[0], n)
        self.emitter.emit_end_less_or_equal()

    def visit_LE(self, n, ctx):
        self.emitter.emit_begin_less_or_equal()
        self.visit(n.children[0], n)
        self.emitter.emit_comma()
        self.visit(n.children[1], n)
        self.emitter.emit_end_less_or_equal()

    def visit_ADD(self, n, ctx):
        if n.children[0].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[0].type, 0) < self.associativities.get('ADD'):
                self.emitter.emit_lparen()
                self.visit(n.children[0], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[0], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[0], n)
            self.emitter.emit_end_float_cast()
        self.emitter.emit_add()
        if n.children[1].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[1].type, 0) < self.associativities.get('ADD'):
                self.emitter.emit_lparen()
                self.visit(n.children[1], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[1], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[1], n)
            self.emitter.emit_end_float_cast()

    def visit_SUB(self, n, ctx):
        if n.children[0].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[0].type, 0) < self.associativities.get('SUB'):
                self.emitter.emit_lparen()
                self.visit(n.children[0], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[0], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[0], n)
            self.emitter.emit_end_float_cast()
        self.emitter.emit_sub()
        if n.children[1].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[1].type, 0) < self.associativities.get('SUB'):
                self.emitter.emit_lparen()
                self.visit(n.children[1], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[1], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[1], n)
            self.emitter.emit_end_float_cast()

    def visit_MUL(self, n, ctx):
        if n.children[0].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[0].type, 0) < self.associativities.get('MUL'):
                self.emitter.emit_lparen()
                self.visit(n.children[0], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[0], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[0], n)
            self.emitter.emit_end_float_cast()
        self.emitter.emit_mul()
        if n.children[1].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[1].type, 0) < self.associativities.get('MUL'):
                self.emitter.emit_lparen()
                self.visit(n.children[1], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[1], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[1], n)
            self.emitter.emit_end_float_cast()

    def visit_DIV(self, n, ctx):
        if n.children[0].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[0].type, 0) < self.associativities.get('DIV'):
                self.emitter.emit_lparen()
                self.visit(n.children[0], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[0], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[0], n)
            self.emitter.emit_end_float_cast()
        self.emitter.emit_div()
        if n.children[1].type in ('ADD', 'SUB', 'MUL', 'DIV', 'NUM'):
            if self.associativities.get(n.children[1].type, 0) < self.associativities.get('DIV'):
                self.emitter.emit_lparen()
                self.visit(n.children[1], n)
                self.emitter.emit_rparen()
            else:
                self.visit(n.children[1], n)
        else:
            self.emitter.emit_begin_float_cast()
            self.visit(n.children[1], n)
            self.emitter.emit_end_float_cast()


    def visit_CON(self, n, ctx):
        if n.children[0].type not in ('STR', 'CON'):
            self.emitter.emit_begin_string_cast()
            self.visit(n.children[0], n)
            self.emitter.emit_end_string_cast()
        else:
            self.visit(n.children[0], n)
        self.emitter.emit_add()
        if n.children[1].type not in ('STR', 'CON'):
            self.emitter.emit_begin_string_cast()
            self.visit(n.children[1], n)
            self.emitter.emit_end_string_cast()
        else:
            self.visit(n.children[1], n)

    def visit(self, n, ctx):
        return n.accept(self, ctx)

    def __call__(self, n):
        return self.visit(n, None)


class JavaScriptCodeEmitter(object):
    escapes = {
        '\\': '\\',
        '"': '"',
        '\'': '\'',
        '\a': 'a',
        '\b': 'b',
        '\f': 'f',
        '\n': 'n',
        '\r': 'r',
        '\t': 't',
        '\v': 'v',
        }

    def __init__(self):
        self.buf = []
 
    def _escape(self, v):
        def fn(g):
            c = g.group(0)
            v = self.escapes.get(c)
            if v is None:
                return u'\\x%x' % ord(c)
            else:
                return u'\\%s' % v
        return re.sub(ur'[\x00-\x1f"\\\x7f]', fn, v)

    def emit_add(self):
        self.buf.append(u'+')

    def emit_div(self):
        self.buf.append(u'/')

    def emit_float(self, v):
        self.buf.append(u'%g' % v)

    def emit_lparen(self):
        self.buf.append(u'(')

    def emit_mul(self):
        self.buf.append(u'*')

    def emit_rparen(self):
        self.buf.append(u')')

    def emit_string(self, v):
        self.buf.append(u'"%s"' % self._escape(v))

    def emit_sub(self):
        self.buf.append(u'-')

    def emit_sym_reference(self, v):
        self.buf.append(u'ctx.sym(')
        self.emit_string(v)
        self.buf.append(u')')

    def emit_var_reference(self, v):
        self.buf.append(u'ctx.var(')
        self.emit_string(v)
        self.buf.append(u')')

    def emit_begin_string_cast(self):
        self.buf.append(u'(""+(')

    def emit_end_string_cast(self):
        self.buf.append(u'))')

    def emit_begin_float_cast(self):
        self.buf.append(u'(0+(')

    def emit_end_float_cast(self):
        self.buf.append(u'))')

    def emit_comma(self):
        self.buf.append(u',')

    def emit_begin_equal(self):
        self.buf.append(u'ctx.equal(')

    def emit_end_equal(self):
        self.buf.append(u')')

    def emit_begin_not_equal(self):
        self.buf.append(u'!ctx.equal(')

    def emit_end_not_equal(self):
        self.buf.append(u')')

    def emit_begin_greater(self):
        self.buf.append(u'ctx.greater(')

    def emit_end_greater(self):
        self.buf.append(u')')

    def emit_begin_less_or_equal(self):
        self.buf.append(u'!ctx.greater(')

    def emit_end_less_or_equal(self):
        self.buf.append(u')')

    def emit_and(self):
        self.buf.append(u'&&')

    def emit_or(self):
        self.buf.append(u'||')

    def emit_not(self):
        self.buf.append(u'!')


def javascript_boolean_op_func_handler(n, ctx, visitor):
    assert n.children[0].type == 'SYM'
    op = n.children[0].value.lower()
    def enclose_if_not_leaf(visitor, n, ctx):
        if n.type in ('VAR', 'SYM', 'NUM', 'STR'):
            visitor.visit(n, ctx)
        else:
            visitor.emitter.emit_lparen()
            visitor.visit(n, ctx)
            visitor.emitter.emit_rparen()

    if op == 'and':
        if len(n.children[1].children) != 2:
            raise ParseError('wrong number of arguments for AND function')
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_and()
        enclose_if_not_leaf(visitor, n.children[1].children[1], n)
        visitor.emitter.emit_rparen()
        return True
    elif op == 'or':
        if len(n.children[1].children) != 2:
            raise ParseError('wrong number of arguments for OR function')
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_or()
        enclose_if_not_leaf(visitor, n.children[1].children[1], n)
        visitor.emitter.emit_rparen()
        return True
    elif op == 'not':
        if len(n.children[1].children) != 1:
            raise ParseError('wrong number of arguments for NOT function')
        visitor.emitter.emit_not()
        visitor.emitter.emit_lparen()
        enclose_if_not_leaf(visitor, n.children[1].children[0], n)
        visitor.emitter.emit_rparen()
        return True

