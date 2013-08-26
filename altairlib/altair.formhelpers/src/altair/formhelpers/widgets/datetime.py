# encoding: utf-8
from wtforms.widgets.core import HTMLString, html_params

__all__ = (
    'build_date_input_japanese_japan',
    'build_time_input_japanese_japan',
    'build_datetime_input_japanese_japan',
    'OurDateWidget',
    'OurDateTimeWidget',
    )

def merge_dict(*dicts):
    retval = dict()
    for dict_ in dicts:
        retval.update(dict_)
    return retval

def build_date_input_japanese_japan(fields, common_attrs={}, id_prefix=u'', name_prefix=u'', class_prefix=u'', year_attrs={}, month_attrs={}, day_attrs={}, **kwargs):
    return [
        u'<span %s><input %s /><span %s>年</span></span>' % (
            html_params(class_=class_prefix + u'year'),
            html_params(class_=class_prefix + u'year',
                        id=id_prefix + u'year',
                        name=name_prefix + u'year',
                        value=fields['year'],
                        size="4",
                        maxlength="4",
                        style="width:5ex",
                        **merge_dict(common_attrs, year_attrs)),
            html_params(class_=class_prefix + u'label')
            ),
        u'<span %s><input %s /><span %s>月</span></span>' % (
            html_params(class_=class_prefix + u'month'),
            html_params(class_=class_prefix + u'month',
                        id=id_prefix + u'month',
                        name=name_prefix + u'month',
                        value=fields['month'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, month_attrs)),
            html_params(class_=class_prefix + u'label')
            ),
        u'<span %s><input %s /><span %s>日</span></span>' % (
            html_params(class_=class_prefix + u'day'),
            html_params(class_=class_prefix + u'day',
                        id=id_prefix + u'day',
                        name=name_prefix + u'day',
                        value=fields['day'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, day_attrs)),
            html_params(class_=class_prefix + u'label')
            ),
        ]

def build_time_input_japanese_japan(fields, common_attrs={}, id_prefix=u'', name_prefix=u'', class_prefix=u'', omit_second=False, hour_attrs={}, minute_attrs={}, second_attrs={}, **kwargs):
    html = [
        u'<span %s><input %s /><span %s>時</span></span>' % (
            html_params(class_=class_prefix + u'hour'),
            html_params(class_=class_prefix + u'hour',
                        id=id_prefix + u'hour',
                        name=name_prefix + u'hour',
                        value=fields['hour'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, hour_attrs)),
            html_params(class_=class_prefix + u'label')
            ),
        u'<span %s><input %s /><span %s>分</span></span>' % (
            html_params(class_=class_prefix + u'minute'),
            html_params(class_=class_prefix + u'minute',
                        id=id_prefix + u'minute',
                        name=name_prefix + u'minute',
                        value=fields['minute'],
                        size="2",
                        maxlength="2",
                        style="width:3ex",
                        **merge_dict(common_attrs, minute_attrs)),
            html_params(class_=class_prefix + u'label')
            ),
        ]
    if not omit_second:
        html.append( 
            u'<span %s><input %s /><span %s>秒</span></span>' % (
                html_params(class_=class_prefix + u'second'),
                html_params(class_=class_prefix + u'second',
                            id=id_prefix + u'second',
                            name=name_prefix + u'second',
                            value=fields['second'],
                            size="2",
                            maxlength="2",
                            style="width:3ex",
                            **merge_dict(common_attrs, second_attrs)),
                html_params(class_=class_prefix + u'label')
                )
            )
    return html

def build_datetime_input_japanese_japan(fields, **kwargs):
    html = build_date_input_japanese_japan(fields,  **kwargs)
    html.extend(build_time_input_japanese_japan(fields, **kwargs))
    return html

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
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}
        return HTMLString(
            u'<span %s>' % html_params(class_=class_prefix + 'container') + \
            u''.join(self.input_builder(
                fields=field._values,
                id_prefix=field.id_prefix,
                name_prefix=field.name_prefix,
                class_prefix=class_prefix,
                omit_second=kwargs.pop('omit_second', False),
                year_attrs={'placeholder': placeholders.get('year', u'')},
                month_attrs={'placeholder': placeholders.get('month', u'')},
                day_attrs={'placeholder': placeholders.get('day', u'')},
                common_attrs=kwargs
                )) + \
            u'</span>'
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

    def __init__(self, input_builder=build_datetime_input_japanese_japan, class_prefix=u'datetimewidget-', placeholders=None):
        self.input_builder = input_builder
        self.class_prefix = class_prefix
        self.placeholders = placeholders

    def __call__(self, field, **kwargs):
        from ..fields.datetime import Automatic
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}
        return HTMLString(
            u'<span %s>' % html_params(class_=class_prefix + 'container') + \
            u''.join(self.input_builder(
                fields=field._values,
                id_prefix=field.id_prefix,
                name_prefix=field.name_prefix,
                class_prefix=class_prefix,
                omit_second=kwargs.pop('omit_second', False),
                year_attrs={'placeholder': placeholders.get('year', u'')},
                month_attrs={'placeholder': placeholders.get('month', u'')},
                day_attrs={'placeholder': placeholders.get('day', u'')},
                hour_attrs={'placeholder': placeholders.get('hour', u'')},
                minute_attrs={'placeholder': placeholders.get('minute', u'')},
                second_attrs={'placeholder': placeholders.get('second', u'')},
                common_attrs=kwargs
                )) + \
            u'</span>'
            )

class OurTimeWidget(object):
    _default_placeholders = dict(
        hour='HH',
        minute='MM',
        second='SS',
        )

    def __init__(self, input_builder=build_time_input_japanese_japan, class_prefix=u'datetimewidget-', placeholders=None):
        self.input_builder = input_builder
        self.class_prefix = class_prefix
        self.placeholders = placeholders

    def __call__(self, field, **kwargs):
        from ..fields.datetime import Automatic
        kwargs.pop('class_', None)
        class_prefix = kwargs.pop('class_prefix', self.class_prefix)
        placeholders = kwargs.pop('placeholders', self.placeholders)
        if placeholders is Automatic:
            placeholders = dict(self._default_placeholders)
            placeholders.update(field.missing_value_defaults)
        if placeholders is None:
            placeholders = {}
        return HTMLString(
            u'<span %s>' % html_params(class_=class_prefix + 'container') + \
            u''.join(self.input_builder(
                fields=field._values,
                id_prefix=field.id_prefix,
                name_prefix=field.name_prefix,
                class_prefix=class_prefix,
                omit_second=kwargs.pop('omit_second', False),
                hour_attrs={'placeholder': placeholders.get('hour', u'')},
                minute_attrs={'placeholder': placeholders.get('minute', u'')},
                second_attrs={'placeholder': placeholders.get('second', u'')},
                common_attrs=kwargs
                )) + \
            u'</span>'
            )

