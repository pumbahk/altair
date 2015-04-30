# encoding: utf-8
import sys
import re
from collections import namedtuple

__all__ = (
    'DSLError',
    'TokenizationError',
    'ParseError',
    'Tokenizer',
    'Parser',
    'pp',
    )

class DSLError(Exception):
    def __init__(self, message, line, column):
        super(Exception, self).__init__(message, line, column)

    @property
    def message(self):
        return self.args[0]

    @property
    def line(self):
        return self.args[1]

    @property
    def column(self):
        return self.args[2]

    def __str__(self):
        return '%s at line %d column %d' % (self.message, self.line, self.column)

class TokenizationError(DSLError):
    pass


def unescape(s):
    def r(g):
        c = g.group(0)
        if c[1] in (u'0', u'1', u'2', u'3', u'4', u'5', u'6', u'7', u'8', u'9'):
            return c
        else:
            return c[1]
    return re.sub(ur'\\.', r, s)

class Tokenizer(object):
    TOKEN_REGEXP = ur'(?:\{([^}]+)\})|([A-Za-z_][0-9A-Za-z_]*)|(<>|<=|>=|=>|=<|<|>|[&(),=+*/-])|(?:"((?:[^"\\]|(?:\\.))*)")|(-?(?:[0-9]+(?:\.[0-9]+)?|\.[0-9]+)(?:[eE][-+]?[0-9]+)?)|([ \t]+)|(\r\n|\r|\n)|(.)'
    def __init__(self, expr):
        self.tokens = re.finditer(self.TOKEN_REGEXP, expr)
        self.eof = False
        self.line = 1
        self.column = 1
        self.stack = []

    def __iter__(self):
        return self

    def pushback(self, t):
        self.stack.append(t)

    def next(self):
        if len(self.stack) > 0:
            return self.stack.pop()
        while not self.eof:
            try:
                token = self.tokens.next()
            except StopIteration:
                self.eof = True
                return ('EOF', None, self.line, self.column)
            t_var = token.group(1)
            t_id = token.group(2)
            t_op = token.group(3)
            t_str = token.group(4)
            t_num = token.group(5)
            t_sp = token.group(6)
            t_newline = token.group(7)
            t_unknown = token.group(8)
            if t_var is not None:
                retval = ('VAR', t_var, self.line, self.column)
                self.column += len(token.group(0))
                return retval
            elif t_id is not None:
                retval = ('ID', t_id, self.line, self.column)
                self.column += len(token.group(0))
                return retval
            elif t_op is not None:
                if t_op == '=<':
                    t_op = '<='
                elif t_op == '=>':
                    t_op = '>='
                retval = (t_op, t_op, self.line, self.column)
                self.column += len(token.group(0))
                return retval
            elif t_str is not None:
                t_str = unescape(t_str)
                retval = ('STR', t_str, self.line, self.column)
                self.column += len(token.group(0))
                return retval
            elif t_num is not None:
                retval = ('NUM', t_num, self.line, self.column)
                self.column += len(token.group(0))
                return retval
            elif t_sp is not None:
                self.column += len(token.group(0))
            elif t_newline is not None:
                self.column = 1
                self.line += 1
            else:
                raise TokenizationError(u'Unexpected character: %s' % t_unknown, self.line, self.column)
        raise StopIteration

class ParseError(DSLError):
    pass

Empty = ()

class Node(object):
    def __init__(self, type, line=0, column=0, value=None, children=Empty):
        self.type = type
        self.line = line
        self.column = column
        self.value = value
        self.children = children
        self._visitor_name = 'visit_%s' % self.type

    def __repr__(self):
        return 'Node(type=%s, line=%d, column=%d, value=%r, children=%r)' % (self.type, self.line, self.column, self.value, self.children)

    def accept(self, visitor, ctx=None):
        return getattr(visitor, self._visitor_name)(self, ctx)

class Parser(object):
    associativities = {
        '=': 1,
        '<>': 1,
        '>': 1,
        '<': 1,
        '>=': 1,
        '<=': 1,
        '&': 2,
        '+': 3,
        '-': 3,
        '*': 4,
        '/': 4,
        }
    node_names = {
        '=': 'EQ',
        '<>': 'NE',
        '>': 'GT',
        '<': 'LT',
        '>=': 'GE',
        '<=': 'LE',
        '&': 'CON',
        '+': 'ADD',
        '-': 'SUB',
        '*': 'MUL',
        '/': 'DIV',
        }
    infix_ops = tuple(associativities)

    def __init__(self, t):
        self.t = t

    def expect(self, t, types):
        if t[0] not in types:
            self.raise_parse_error(t, types)

    def raise_parse_error(self, t, types):
        raise ParseError(u'%s expected, got %s' % (u', '.join(types), t[0]), t[2], t[3])

    def parse_function_call_args(self):
        args = []
        while True:
            n, t = self.parse_expr((')', ','))
            if n is not None:
                args.append(n)
            if t[0] == ')':
                break
        return args

    def parse_comp(self, expects=None):
        t0 = self.t.next()
        if t0[0] == '(':
            return self.parse_expr((')',))
        elif t0[0] in ('VAR', 'STR'):
            return Node(type=t0[0], line=t0[2], column=t0[3], value=t0[1]), None
        elif t0[0] == 'NUM':
            try:
                return Node(type=t0[0], line=t0[2], column=t0[3], value=float(t0[1])), None
            except (TypeError, ValueError) as e:
                raise ParseError(u'Invalid number: %s' % t0[1], line=t0[2], column=t0[3])
        elif t0[0] == 'ID':
            n = Node(type='SYM', line=t0[2], column=t0[3], value=t0[1])
            t1 = self.t.next()
            if t1[0] == '(':
                return (
                    Node(
                        type='CALL',
                        line=t0[2],
                        column=t0[3],
                        children=(
                            n,
                            Node(
                                type='TUPLE',
                                line=t1[2],
                                column=t1[3],
                                children=tuple(self.parse_function_call_args())
                                )
                            )
                        ),
                    None
                    )
            else:
                self.t.pushback(t1)
                return n, None
        else:
            if expects is None or t0[0] not in expects:
                _expects = ('ID', 'VAR', 'STR', 'NUM', '(')
                if expects is not None:
                    _expects += expects
                self.raise_parse_error(t0, _expects)
            return None, t0

    def parse_expr_infix_left(self, n, expects=None):
        t = self.t.next()
        while True:
            if t[0] not in self.infix_ops:
                if expects is not None and t[0] not in expects:
                    self.raise_parse_error(t, self.infix_ops + expects)
                break
            else:
                nr, _ = self.parse_comp()
                tn = self.t.next()
                # check if any infix operator follows
                if self.associativities[t[0]] < self.associativities.get(tn[0], 0):
                    self.t.pushback(tn)
                    nr, tn = self.parse_expr_infix_left(nr)
                    n = Node(
                        type=self.node_names[t[0]],
                        line=t[2],
                        column=t[3],
                        children=(n, nr)
                        )
                else:
                    n = Node(
                        type=self.node_names[t[0]],
                        line=t[2],
                        column=t[3],
                        children=(n, nr)
                        )
                t = tn
        return n, t

    def parse_expr(self, expects=None):
        n, t = self.parse_comp(expects)
        if n is None:
            return n, t
        else:
            return self.parse_expr_infix_left(n, expects)

    def __call__(self):
        return self.parse_expr(('EOF',))[0]


def pp(n, indent='', out=sys.stdout):
    lines = []
    lines.append('- type: %s' % n.type)
    lines.append('  line: %d' % n.line)
    lines.append('  column: %d' % n.column)
    if n.value is not None:
        lines.append('  value: %r' % n.value)
    for l in lines:
        out.write(indent + l + '\n')
    if n.children is not None:
        out.write(indent + '  children:\n')
        for cn in n.children:
            pp(cn, indent=(indent + '  '), out=out)
    if indent == '':
        out.flush()

class Visitor(object):
    def visit_NUM(self, n, ctx):
        pass

    def visit_STR(self, n, ctx):
        pass

    def visit_VAR(self, n, ctx):
        pass

    def visit_SYM(self, n, ctx):
        pass

    def visit_CALL(self, n, ctx):
        pass

    def visit_TUPLE(self, n, ctx):
        pass

    def visit_EQ(self, n, ctx):
        pass

    def visit_NE(self, n, ctx):
        pass

    def visit_GT(self, n, ctx):
        pass

    def visit_LT(self, n, ctx):
        pass

    def visit_GE(self, n, ctx):
        pass

    def visit_LE(self, n, ctx):
        pass

    def visit_ADD(self, n, ctx):
        pass

    def visit_SUB(self, n, ctx):
        pass

    def visit_MUL(self, n, ctx):
        pass

    def visit_DIV(self, n, ctx):
        pass

    def visit_CON(self, n, ctx):
        pass

    def visit(self, n, ctx):
        return n.accept(self, ctx)

    def __call__(self, n):
        return self.visit(n, None)

