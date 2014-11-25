class NodeVisitor(object):
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

    def visit_NEQ(self, n, ctx):
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


class PythonCodeEmitter(object):
    def emit_add(self):
        pass

    def emit_div(self):
        pass

    def emit_float(self, v):
        pass

    def emit_lparen(self):
        pass

    def emit_mul(self):
        pass

    def emit_rparen(self):
        pass

    def emit_string(self, v):
        pass

    def emit_sub(self):
        pass

    def emit_sym_reference(self, v):
        pass

    def emit_var_reference(self, v):
        pass

    def emit_begin_string_cast(self):
        pass

    def emit_end_string_cast(self):
        pass

    def emit_begin_float_cast(self):
        pass

    def emit_end_float_cast(self):
        pass

    def emit_comma(self):
        pass

    def emit_begin_equal(self):
        pass

    def emit_end_equal(self):
        pass

    def emit_begin_not_equal(self):
        pass

    def emit_end_not_equal(self):
        pass

    def emit_begin_greater(self):
        pass

    def emit_end_greater(self):
        pass

    def emit_begin_less_or_equal(self):
        pass

    def emit_end_less_or_equal(self):
        pass

    def emit_and(self):
        pass

    def emit_or(self):
        pass

    def emit_not(self):
        pass
