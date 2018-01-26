# encoding: utf-8
from __future__ import absolute_import
import json
from wtforms.widgets.core import HTMLString, html_params
from .context import Rendrant
from datetime import datetime

__all__ = (
    'build_date_input_japanese_japan',
    'build_date_input_select_japanese_japan',
    'build_time_input_japanese_japan',
    'build_datetime_input_japanese_japan',
    'build_date_input_select_i18n',
    'OurDateWidget',
    'OurDateTimeWidget',
    )

def merge_dict(*dicts):
    retval = dict()
    for dict_ in dicts:
        retval.update(dict_)
    return retval

class InputBuilderContext(object):
    def __init__(self, buf):
        self.buf = buf
        self.field_ids = dict(
            year=None,
            month=None,
            day=None,
            hour=None,
            minute=None,
            second=None
            )

class DateInputFormElementBuilder(object):
    def year(self, id_, name, value, **kwargs):
        return u'<input %s />' % \
            html_params(
                id=id_,
                name=name,
                value=value,
                size="4",
                maxlength="4",
                style="width:5ex",
                **kwargs
                )

    def month(self, id_, name, value, **kwargs):
        return u'<input %s />' % \
            html_params(
                id=id_,
                name=name,
                value=value,
                size="2",
                maxlength="2",
                style="width:3ex",
                **kwargs
                )

    def day(self, id_, name, value, **kwargs):
        return u'<input %s />' % \
            html_params(
                id=id_,
                name=name,
                value=value,
                size="2",
                maxlength="2",
                style="width:3ex",
                **kwargs
                )

class DateSelectFormElementBuilder(object):
    def __init__(self, year_lower_bound=1900, year_upper_bound=None, placeholders=False):
        self.year_lower_bound = year_lower_bound
        self.year_upper_bound = year_upper_bound or (lambda: datetime.now().year)
        self.placeholders = placeholders

    def _build_year_options(self, value):
        year_upper_bound = self.year_upper_bound
        if callable(year_upper_bound):
            year_upper_bound = year_upper_bound()
        buf = []
        if self.placeholders:
            buf.append(u'<option value="">----</option>')
        for i in range(self.year_lower_bound, year_upper_bound + 1):
            if i == value:
                buf.append(u'<option value="%d" selected="selected">' % i)
            else:
                buf.append(u'<option value="%d">' % i)
            buf.append(u'%d</option>' % i)
        return u''.join(buf)

    def _build_month_options(self, value):
        buf = []
        if self.placeholders:
            buf.append(u'<option value="">--</option>')
        for i in range(1, 13):
            if i == value:
                buf.append(u'<option selected="selected">')
            else:
                buf.append(u'<option>')
            buf.append(u'%d</option>' % i)
        return u''.join(buf)

    def _build_day_options(self, value):
        buf = []
        if self.placeholders:
            buf.append(u'<option value="">--</option>')
        for i in range(1, 32):
            if i == value:
                buf.append(u'<option selected="selected">')
            else:
                buf.append(u'<option>')
            buf.append(u'%d</option>' % i)
        return u''.join(buf)

    def year(self, id_, name, value, **kwargs):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None
        return u'<select %s>%s</select>' % (
            html_params(
                id=id_,
                name=name,
                **kwargs
                ),
            self._build_year_options(value)
            )

    def month(self, id_, name, value, **kwargs):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None
        return u'<select %s>%s</select>' % (
            html_params(
                id=id_,
                name=name,
                **kwargs
                ),
            self._build_month_options(value)
            )

    def day(self, id_, name, value, **kwargs):
        try:
            value = int(value)
        except (TypeError, ValueError):
            value = None
        return u'<select %s>%s</select>' % (
            html_params(
                id=id_,
                name=name,
                **kwargs
                ),
            self._build_day_options(value)
            )


class DateFieldBuilder(object):
    def __init__(self, form_element_builder, i18n=False):
        self.form_element_builder = form_element_builder
        self.i18n = i18n

    def __call__(self, ctx, fields, common_attrs={}, id_prefix=u'', name_prefix=u'', class_prefix=u'', year_attrs={}, month_attrs={}, day_attrs={}, **kwargs):
        ctx.buf.append(u'<span %s>' % html_params(class_=class_prefix + u'year'))
        year_field_id = id_prefix + u'year'
        ctx.buf.append(self.form_element_builder.year( 
            id_=year_field_id,
            name=name_prefix + u'year',
            value=fields['year'],
            class_=class_prefix + u'year',
            **merge_dict(common_attrs, year_attrs)
            ))
        if self.i18n:
            ctx.buf.append(u'<span %s>year</span></span>' % html_params(class_=class_prefix + u'label'))
        else:
            ctx.buf.append(u'<span %s>年</span></span>' % html_params(class_=class_prefix + u'label'))
        ctx.field_ids['year'] = year_field_id

        month_field_id = id_prefix + u'month'
        ctx.buf.append(u'<span %s>' % html_params(class_=class_prefix + u'month'))
        ctx.buf.append(self.form_element_builder.month( 
            id_=month_field_id,
            name=name_prefix + u'month',
            value=fields['month'],
            class_=class_prefix + u'month',
            **merge_dict(common_attrs, month_attrs)
            ))
        if self.i18n:
            ctx.buf.append(u'<span %s>month</span></span>' % html_params(class_=class_prefix + u'label'))
        else:
            ctx.buf.append(u'<span %s>月</span></span>' % html_params(class_=class_prefix + u'label'))
        ctx.field_ids['month'] = month_field_id

        day_field_id = id_prefix + u'day'
        ctx.buf.append(u'<span %s>' % html_params(class_=class_prefix + u'day'))
        ctx.buf.append(self.form_element_builder.day( 
            id_=day_field_id,
            name=name_prefix + u'day',
            value=fields['day'],
            class_=class_prefix + u'day',
            **merge_dict(common_attrs, day_attrs)
            ))
        if self.i18n:
            ctx.buf.append(u'<span %s>day</span></span>' % html_params(class_=class_prefix + u'label'))
        else:
            ctx.buf.append(u'<span %s>日</span></span>' % html_params(class_=class_prefix + u'label'))
        ctx.field_ids['day'] = day_field_id

build_date_input_japanese_japan = DateFieldBuilder(DateInputFormElementBuilder())
build_date_input_select_japanese_japan = DateFieldBuilder(DateSelectFormElementBuilder())
build_date_input_select_i18n = DateFieldBuilder(DateSelectFormElementBuilder(), True)

def build_time_input_japanese_japan(ctx, fields, common_attrs={}, id_prefix=u'', name_prefix=u'', class_prefix=u'', omit_second=False, hour_attrs={}, minute_attrs={}, second_attrs={}, **kwargs):
    hour_field_id = id_prefix + u'hour'
    ctx.buf.append(
        u'<span %s><input %s /><span %s>時</span></span>' % (
            html_params(class_=class_prefix + u'hour'),
            html_params(class_=class_prefix + u'hour',
                        id=hour_field_id,
                        name=name_prefix + u'hour',
                        value=fields['hour'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, hour_attrs)),
            html_params(class_=class_prefix + u'label')
            )
        )
    ctx.field_ids['hour'] = hour_field_id

    minute_field_id = id_prefix + u'minute'
    ctx.buf.append(
        u'<span %s><input %s /><span %s>分</span></span>' % (
            html_params(class_=class_prefix + u'minute'),
            html_params(class_=class_prefix + u'minute',
                        id=minute_field_id,
                        name=name_prefix + u'minute',
                        value=fields['minute'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, minute_attrs)),
            html_params(class_=class_prefix + u'label')
            )
        )
    ctx.field_ids['minute'] = minute_field_id

    if not omit_second:
        second_field_id = id_prefix + u'second'
        ctx.buf.append(
            u'<span %s><input %s /><span %s>秒</span></span>' % (
                html_params(class_=class_prefix + u'second'),
                html_params(class_=class_prefix + u'second',
                            id=second_field_id,
                            name=name_prefix + u'second',
                            value=fields['second'],
                            size="2",
                            maxlength="2",
                            style="width:3ex",
                            **merge_dict(common_attrs, second_attrs)),
                html_params(class_=class_prefix + u'label')
                )
            )
        ctx.field_ids['second'] = second_field_id

def build_datetime_input_japanese_japan(ctx, fields, **kwargs):
    build_date_input_japanese_japan(ctx, fields,  **kwargs)
    build_time_input_japanese_japan(ctx, fields, **kwargs)


class DateTimeWidgetRendrant(Rendrant):
    def __init__(self, field, html, field_specs, coercer):
        super(DateTimeWidgetRendrant, self).__init__(field, html)
        self.field_specs = field_specs
        self.coercer = coercer

    def render_js_data_provider(self, registry_var_name):
        coercer = self.coercer
        if callable(coercer):
            coercer = coercer()
        return u'''<script type="text/javascript">
(function(name, field_ids, coercer) {
  var ns = [];
  var nmap = {};
  var dummy = { value: null };
  for (var k in field_ids) {
    var id = field_ids[k];
    var n = null;
    if (id !== null) {
      n = document.getElementById(id);
      ns.push(n);
    } else {
      n = dummy;
    }
    nmap[k] = n;
  }
  window[%(registry_var_name)s].registerProvider(name, {
    getValue: function () {
      return coercer({
        'year': nmap['year'].value,
        'month': nmap['month'].value,
        'day': nmap['day'].value,
        'hour': nmap['hour'].value,
        'minute': nmap['minute'].value,
        'second': nmap['second'].value
      });
    },
    getUIElements: function () {
      return ns;
    }
  });
})(%(name)s, %(field_specs)s, %(coercer)s);
</script>''' % dict(name=json.dumps(self.field.short_name), field_specs=json.dumps(self.field_specs), coercer=coercer, registry_var_name=json.dumps(registry_var_name))

def build_field_specs(field, field_ids):
    retval = {}
    for k in ['year', 'month', 'day', 'hour', 'minute', 'second']:
        default = field.value_defaults[k]
        if callable(default):
            default = default()    
        retval[k] = {
            u'id': field_ids[k],
            u'default': default,
            }
    return retval

class OurDateWidget(object):
    _default_placeholders = dict(
        year='YYYY',
        month='MM',
        day='DD',
        )

    def __init__(self, input_builder=build_date_input_japanese_japan, class_prefix=u'datetimewidget-', placeholders=None):
        self.input_builder = input_builder
        self.class_prefix = class_prefix
        self.placeholders = placeholders

    def __call__(self, field, **kwargs):
        from ..fields.datetime import Automatic
        kwargs.pop('context', None)
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}

        buf = []
        buf.append(u'<span %s>' % html_params(class_=class_prefix + 'container'))
        ctx = InputBuilderContext(buf)
        self.input_builder(
            ctx,
            fields=field._values,
            id_prefix=field.id_prefix,
            name_prefix=field.name_prefix,
            class_prefix=class_prefix,
            omit_second=kwargs.pop('omit_second', False),
            year_attrs={'placeholder': placeholders.get('year', u'')},
            month_attrs={'placeholder': placeholders.get('month', u'')},
            day_attrs={'placeholder': placeholders.get('day', u'')},
            common_attrs=kwargs
            )
        buf.append(u'</span>')
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is None:
            js_coercer = u"function (v) { return new Date(parseInt(v['year']), parseInt(v['month']) - 1, parseInt(v['day']), 0, 0, 0); }"
        return DateTimeWidgetRendrant(
            field,
            u''.join(buf),
            ctx.field_ids,
            js_coercer
            )


class OurDateTimeWidget(object):
    _default_placeholders = dict(
        year='YYYY',
        month='MM',
        day='DD',
        hour='HH',
        minute='MM',
        second='SS',
        )

    def __init__(self, input_builder=build_datetime_input_japanese_japan, class_prefix=u'datetimewidget-', placeholders=None, omit_second=False):
        self.input_builder = input_builder
        self.class_prefix = class_prefix
        self.placeholders = placeholders
        self.omit_second = omit_second

    def __call__(self, field, **kwargs):
        from ..fields.datetime import Automatic
        kwargs.pop('context', None)
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}
        buf = []
        buf.append(u'<span %s>' % html_params(class_=class_prefix + 'container'))
        ctx = InputBuilderContext(buf)
        self.input_builder(
            ctx,
            fields=field._values,
            id_prefix=field.id_prefix,
            name_prefix=field.name_prefix,
            class_prefix=class_prefix,
            omit_second=kwargs.pop('omit_second', self.omit_second),
            year_attrs={'placeholder': placeholders.get('year', u'')},
            month_attrs={'placeholder': placeholders.get('month', u'')},
            day_attrs={'placeholder': placeholders.get('day', u'')},
            hour_attrs={'placeholder': placeholders.get('hour', u'')},
            minute_attrs={'placeholder': placeholders.get('minute', u'')},
            second_attrs={'placeholder': placeholders.get('second', u'')},
            common_attrs=kwargs
            )
        buf.append(u'</span>')
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is None:
            js_coercer = u"function (v) { return new Date(parseInt(v['year']), parseInt(v['month']) - 1, parseInt(v['day']), parseInt(v['hour']), parseInt(v['minute']), parseInt(v['second'])); }"
        return DateTimeWidgetRendrant(
            field,
            u''.join(buf),
            ctx.field_ids,
            js_coercer
            )


class OurTimeWidget(object):
    _default_placeholders = dict(
        hour='HH',
        minute='MM',
        second='SS',
        )

    def __init__(self, input_builder=build_time_input_japanese_japan, class_prefix=u'datetimewidget-', placeholders=None, omit_second=False):
        self.input_builder = input_builder
        self.class_prefix = class_prefix
        self.placeholders = placeholders
        self.omit_second = omit_second

    def __call__(self, field, **kwargs):
        from ..fields.datetime import Automatic
        kwargs.pop('context', None)
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}
        buf = []
        buf.append(u'<span %s>' % html_params(class_=class_prefix + 'container'))
        ctx = InputBuilderContext(buf)
        self.input_builder(
            ctx,
            fields=field._values,
            id_prefix=field.id_prefix,
            name_prefix=field.name_prefix,
            class_prefix=class_prefix,
            omit_second=kwargs.pop('omit_second', self.omit_second),
            hour_attrs={'placeholder': placeholders.get('hour', u'')},
            minute_attrs={'placeholder': placeholders.get('minute', u'')},
            second_attrs={'placeholder': placeholders.get('second', u'')},
            common_attrs=kwargs
            )
        buf.append(u'</span>')
        js_coercer = getattr(field, 'build_js_coercer', None)
        if js_coercer is None:
            js_coercer = u"function (v) { return { getHours: function () { return parseInt(v['hour']) }, getMinutes: function () { return parseInt(v['minute']) }, getSeconds: function () { return parseInt(v['second']) } } }"
        return DateTimeWidgetRendrant(
            field,
            u''.join(buf),
            ctx.field_ids,
            js_coercer
            )

