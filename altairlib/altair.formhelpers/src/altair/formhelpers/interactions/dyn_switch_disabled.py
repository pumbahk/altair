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

def build_dyn_switch_disabled_js(rendering_context, registry_var):
    dyn_switches = {}
    for name, rendrant in rendering_context.rendrants.items():
        validators = [validator for validator in rendrant.field.validators if isinstance(validator, DynSwitchDisabled)]
        if validators:
            dyn_switches[name] = validators
    retval = []
    retval.append(u'''<script type="text/javascript">
(function (registry) {
  var providers = registry.providers;
''')
    retval.append(u'''  var Context = function(sym) { if (sym) this.sym = sym; };
  Context.prototype = {
    var: function (name) {
      return providers[name].getValue();
    },
    sym: function (_) { return null },
    _cast: function (l, r) {
      if (typeof l == 'number')
        r = 0 + r;
      else if (typeof h == 'number')
        l = 0 + l;
      return [l, r];
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
    }
  };
''')
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
        } else {
          var f = builtinFunctions[name];
          if (f !== void(0)) {
            return f;
          }
        }
        return null;
      });
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
    })(%(name)s, %(predicate)s)''' % dict(name=json.dumps(name), predicate=predicate))
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
  for (var i in stateChangeHandlers) {
    stateChangeHandlers[i]();
  }
''' % dict(name=json.dumps(dependent_on_var), dependants=json.dumps(dependants)))
    retval.append(u'''})(%(registry_var)s);
</script>''' % dict(registry_var=registry_var))
    return u''.join(retval)
