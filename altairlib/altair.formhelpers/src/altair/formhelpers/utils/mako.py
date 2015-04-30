from __future__ import absolute_import

import json
from uuid import uuid4
import functools
from wtforms.widgets.core import HTMLString
from mako.runtime import supports_caller as _supports_caller
from altair.formhelpers.widgets.context import RenderingContext
from altair.formhelpers.interactions import dyn_switch_disabled as dso
from .javascript import DateTimeEncodingJavaScriptEncoder

def supports_caller(func):
    return functools.wraps(func)(_supports_caller(func))

@supports_caller
def render_block(context, *args, **kwargs):
    prev_render_context = context._kwargs.get('rendering_context')
    try:
        rendering_context = RenderingContext()
        context._kwargs['rendering_context'] = rendering_context
        registry_var_name = u'\'%s-%s' % (__name__, uuid4())
        context._kwargs['registry_var_name'] = registry_var_name
        encoded_registry_var_name = json.dumps(registry_var_name)
        context.write(u'''<script type="text/javascript">
window[%s] = {
  providers: {},
  registerProvider: function(name, provider) {
    this.providers[name] = provider;
  }
};
</script>
''' % encoded_registry_var_name)
        context['caller'].body()
        for k, v in rendering_context.rendrants.items():
            context.write(v.render_js_data_provider(registry_var_name))
        post = getattr(context['caller'], '__post__')
        if post is not None:
            post(u'window[%s]' % encoded_registry_var_name)
    finally:
        context._kwargs['rendering_context'] = prev_render_context
    return u''

def render(context, render, **kwargs):
    rendering_context = context._kwargs.get('rendering_context')
    if rendering_context is not None:
        return rendering_context.render(render, **kwargs)
    else:
        return render(**kwargs)

def inject_js(context, registry_var, predefined_symbols={}, js_serializer=None, **kwargs):
    if js_serializer is None:
        js_serializer = DateTimeEncodingJavaScriptEncoder(ensure_ascii=False).encode
    retval = []
    retval.append(dso.build_dyn_switch_disabled_js(context._kwargs['rendering_context'], registry_var, predefined_symbols, js_serializer))
    return HTMLString(u''.join(retval))
