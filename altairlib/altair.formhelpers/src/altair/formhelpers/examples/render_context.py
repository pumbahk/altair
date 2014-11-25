import cgi
from altair.formhelpers.form import OurForm
from altair.formhelpers.fields import OurSelectField, OurTextField, OurIntegerField, OurDateTimeField
from altair.formhelpers.validators import Required, DynSwitchDisabled
from altair.formhelpers.interactions.dyn_switch_disabled import build_dyn_switch_disabled_js
from mako.template import Template
from mako.runtime import Context, ModuleNamespace
from mako.util import FastEncodingBuffer
from wtforms.widgets.core import HTMLString
import functools

template = Template(u'''<!DOCTYPE html>
<html>
<body>
<form method="POST">
  <dl>
    <dt>select</dt>
    <dd>${form.select.data}</dd>
    <dt>text</dt>
    <dd>${form.text.data}</dd>
    <dt>integer</dt>
    <dd>${form.integer.data}</dd>
    <dt>datetime</dt>
    <dd>${form.datetime.data}</dd>
    <dt>datetime2</dt>
    <dd>${form.datetime2.data}</dd>
  </dl>
  <%n:render_block>
    <div>
      <div>${n.render(form.select)}</div>
      <div>${n.errors(form.select.errors)}</div>
    </div>
    <div>
      <div>${n.render(form.text)}</div>
      <div>${n.errors(form.text.errors)}</div>
    </div>
    <div>
      <div>${n.render(form.integer)}</div>
      <div>${n.errors(form.integer.errors)}</div>
    </div>
    <div>
      <div>${n.render(form.datetime)}</div>
      <div>${n.errors(form.datetime.errors)}</div>
    </div>
    <div>
      <div>${n.render(form.datetime2)}</div>
      <div>${n.errors(form.datetime2.errors)}</div>
    </div>
    <input type="submit" />
    <%def name="__post__(registry_var)">
    ${n.post(registry_var)|n}
    </%def>
  </%n:render_block>
</form>
</body>
</html>
''')

class DemoForm(OurForm):
    select = OurSelectField(
        choices=[
            ('1', 'A'),
            ('2', 'B'),
            ('3', 'C'),
            ]
        )
    text = OurTextField(
        validators=[
            DynSwitchDisabled(u'{select} <> 3'),
            Required(),
            ]
        )
    integer = OurIntegerField()
    datetime = OurDateTimeField(
        validators=[
            DynSwitchDisabled(u'{integer} > 0'),
            Required(),
            ]
        )
    datetime2 = OurDateTimeField(
        validators=[
            DynSwitchDisabled(u'YEAR({datetime}) >= 1990'),
            Required(),
            ]
        )

def errors(l):
    retval = [u'<ul>']
    for i in l:
        retval.append(u'<li>%s</li>' % cgi.escape(i))
    retval.append(u'</li>')
    return HTMLString(u''.join(retval))

def post(context, registry_var):
    return build_dyn_switch_disabled_js(context['rendering_context'], registry_var)

def app(environ, start_response):
    fields = cgi.FieldStorage(environ['wsgi.input'], environ=environ)
    form = DemoForm(fields)
    form.validate()
    buf = FastEncodingBuffer(encoding='UTF-8', errors=template.encoding_errors)
    ctx = Context(buf, form=form)
    n = ModuleNamespace('n', ctx, 'altair.formhelpers.utils.mako')
    n.errors = errors
    n.post = lambda *args, **kwargs: post(ctx, *args, **kwargs)
    ctx._data['n'] = n
    template.render_context(ctx)
    retval = ctx._pop_buffer().getvalue()
    start_response('200 OK', [('Content-Type', 'text/html; charset=UTF-8'), ('Content-Length', '%d' % len(retval))])
    return retval

if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    server = make_server('', 8000, app)
    server.serve_forever()

