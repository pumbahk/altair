# encoding: utf-8

import types
from datetime import datetime, date
from wtforms import validators
from altair.dynpredicate.utils import compile_predicate_to_pycode, compile_predicate_to_ast, eval_compiled_predicate
from altair.dynpredicate.eval import Caster

__all__ = (
    'SwitchOptional',
    'SwitchOptionalBase',
    'DynSwitchOptional',
    'DynSwitchDisabled',
    'CompatibleCaster',
    )

class SwitchOptionalBase(validators.Optional):
    field_flags = ('optional', )

    def __init__(self, predicate=lambda form, field:True, strip_whitespace=True):
        super(SwitchOptionalBase, self).__init__(strip_whitespace=strip_whitespace)
        self.predicate = predicate

    def __call__(self, form, field):
        if self.predicate(form, field):
            super(SwitchOptionalBase, self).__call__(form, field)

class SwitchOptional(SwitchOptionalBase):
    """
    :param switch_field:
        If field named `switch_field` is True, this field marked as optional.
    :param strip_whitespace:
        If True (the default) also stop the validation chain on input which
        consists of only whitespace.
    """
    def __init__(self, switch_field, strip_whitespace=True):
        super(SwitchOptional, self).__init__(
            predicate=lambda form, field: bool(form[switch_field].data),
            strip_whitespace=strip_whitespace
            )

class CompatibleCaster(Caster):
    def to_float(self, o):
        if isinstance(o, datetime):
            v = o - datetime(1900, 1, 1, 0, 0, 0)
            return v.days + 1 + v.seconds / 86400.
        elif isinstance(o, date):
            v = o - datetime(1900, 1, 1)
            return v.days + 1
        else:
            return super(CompatibleCaster, self).to_float(o)

class DynSwitchMixin(object):
    def _sym_THIS(self, form, field):
        return field.data

    @staticmethod
    def _sym_YEAR(v):
        return v.year if v is not None else None

    @staticmethod
    def _sym_MONTH(v):
        return v.month if v is not None else None

    @staticmethod
    def _sym_DAY(v):
        return v.day if v is not None else None

    @staticmethod
    def _sym_NOW():
        return datetime.now()

    def _resolve_sym(self, form, field):
        def _(n):
            f = getattr(self, '_sym_%s' % n, None)
            if f is not None:
                if isinstance(f, types.FunctionType):
                    return f
                else:
                    return f(form, field)
            else:
                if hasattr(form, '_dynswitch_predefined_symbols'):
                    predefined_symbols = form._dynswitch_predefined_symbols
                    if n in predefined_symbols:
                        return predefined_symbols[n]
            return None
        return _

    def _predicate(self, form, field):
        return eval_compiled_predicate(
            self.predicate_code,
            var_resolver=lambda n:form[n].data,
            sym_resolver=self._resolve_sym(form, field),
            caster=CompatibleCaster()
            )

class DynSwitchOptional(SwitchOptionalBase, DynSwitchMixin):
    def __init__(self, predicate_expr, strip_whitespace=True):
        self.predicate_ast = compile_predicate_to_ast(predicate_expr)
        self.predicate_code = compile_predicate_to_pycode(self.predicate_ast)
        super(DynSwitchOptional, self).__init__(
            predicate=self._predicate,
            strip_whitespace=strip_whitespace
            )


class DynSwitchDisabled(DynSwitchMixin):
    def __init__(self, predicate_expr, strip_whitespace=True):
        self.predicate_ast = compile_predicate_to_ast(predicate_expr)
        self.predicate_code = compile_predicate_to_pycode(self.predicate_ast)

    def __call__(self, form, field):
        if self._predicate(form, field):
            field.raw_data = u''
            field.data = None
            del field.errors[:]
            raise validators.StopValidation()
