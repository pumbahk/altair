from __future__ import absolute_import

import json
from altair.dynpredicate.utils import iterate_variables
from altair.dynpredicate.emitters import JavaScriptCodeEmitter, javascript_boolean_op_func_handler, GenericCodeEmittingVisitor

from ..validators import DynSwitchDisabled

def build_js_from_predicates(asts):
    emit = JavaScriptCodeEmitter()
    for i, ast in enumerate(asts):
        if i > 0:
            emit.emit_and()
        emit.emit_lparen()
        GenericCodeEmittingVisitor(emit, javascript_boolean_op_func_handler)(ast)
        emit.emit_rparen()
    emit.buf.insert(0, u'function (ctx) { return ')
    emit.buf.append(u'; }')
    return u''.join(emit.buf)

def build_dyn_switch_disabled_js(rendering_context, registry_var, predefined_symbols={}, js_serializer=None):
    if js_serializer is None:
        js_serializer = json.dumps
    dyn_switches = {}
    for name, rendrant in rendering_context.rendrants.items():
        validators = [validator for validator in rendrant.field.validators if isinstance(validator, DynSwitchDisabled)]
        if validators:
            dyn_switches[name] = validators
    retval = []
    retval.append(u'''<script type="text/javascript">
(function (registry) {
  var providers = registry.providers;
  function daysSince19000100(v) {
    return 25568. + v.getTime() / 86400000.;
  }
''')
    retval.append(u'''  var Context = function(sym) { if (sym) this.sym = sym; };
  Context.prototype = {
    var: function (name) {
      return providers[name].getValue();
    },
    sym: function (_) { return null },
    _toNumber: function (v) {
      if (v instanceof Date)
        return daysSince19000100(v);
      else
        return +v;
    },
    _toString: function (v) {
      if (v === null || v === void(0))
        return "";
      else
        return v.toString();
    },
    _cast: function (l, r) {
      var _l = this._toNumber(l),
          _r = this._toNumber(r);
      if (!isNaN(_l) && !isNaN(_r))
        return [_l, _r];
      return [this._toString(l), this._toString(r)];
    },
    equal: function (l, r) {
      var p = this._cast(l, r);
      return p[0] == p[1];
    },
    greater: function (l, r) {
      var p = this._cast(l, r);
      return p[0] > p[1];
    }
  };
  var builtinFunctions = {
    YEAR: function (v) {
      return v.getYear() + 1900;
    },
    MONTH: function (v) {
      return v.getMonth() + 1;
    },
    DAY: function (v) {
      return v.getDate();
    },
    NOW: function () {
      return new Date();
    },
    DATE: function (year, month, day, hour, minute, second) {
      return new Date(
        year, month - 1, day,
        hour || 0,
        minute || 0,
        second || 0
      );
    }
  };
''')
    retval.append(u'''  var symbolsFactory = function(ctx) { return %(symbols)s; };
''' % dict(symbols=js_serializer(predefined_symbols)))
    retval.append(u'''  var stateChangeHandlers = {
''')
    for i, (name, validators) in enumerate(dyn_switches.items()):
        if i > 0:
            retval.append(u',\n')
        predicate = build_js_from_predicates((validator.predicate_ast for validator in validators))
        retval.append(u'''    %(name)s: (function (name, predicate) {
      var provider = providers[name];
      var elements = provider.getUIElements();
      var ctx = new Context(function (name) {
        if (name == 'THIS') {
          return provider.getValue();
        }
        var v = symbols[name];
        if (v !== void(0)) {
          return v;
        }
        var f = builtinFunctions[name];
        if (f !== void(0)) {
          return f;
        }
        return null;
      });
      var symbols = symbolsFactory(ctx);
      return function () {
        if (predicate(ctx)) {
          for (var i = 0; i < elements.length; i++) {
            elements[i].setAttribute("disabled", "disabled");
          }
        } else {
          for (var i = 0; i < elements.length; i++) {
            elements[i].removeAttribute("disabled");
          }
        }
      };
    })(%(name)s, %(predicate)s)''' % dict(name=js_serializer(name), predicate=predicate))
    retval.append(u'\n  };\n')
    dependencies_rev_map = {}
    for name, validators in dyn_switches.items():
        for validator in validators:
            for dependent_on_var in iterate_variables(validator.predicate_ast):
                dependencies_rev_map.setdefault(dependent_on_var, []).append(name)
    for dependent_on_var, dependants in dependencies_rev_map.items():
        retval.append(u'''  (function (name, dependants) {
    var elements = providers[name].getUIElements();
    for (var i = 0; i < elements.length; i++) {
      elements[i].onchange = function () {
        for (var j = 0; j < dependants.length; j++)
          stateChangeHandlers[dependants[j]]();
      };
    }
  })(%(name)s, %(dependants)s);
''' % dict(name=js_serializer(dependent_on_var), dependants=js_serializer(dependants)))
    retval.append(u'''
  for (var i in stateChangeHandlers) {
    stateChangeHandlers[i]();
  }
})(%(registry_var)s);
</script>''' % dict(registry_var=registry_var))
    return u''.join(retval)
