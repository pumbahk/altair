# -*- coding:utf-8 -*-

import re
from datetime import datetime, date
from exceptions import ValueError
import unicodedata

from wtforms import validators, fields
from wtforms.form import Form, WebobInputWrapper
from wtforms.fields.core import UnboundField, _unset_value
from wtforms.compat import iteritems
from wtforms.widgets.core import HTMLString, Input, html_params
from ticketing.utils import atom, days_of_month
import logging
import warnings

logger = logging.getLogger(__name__)

class BugFreeSelectField(fields.SelectField):
    def pre_validate(self, form):
        for v, _ in self.choices:
            if self.data == self.coerce(v):
                break
        else:
            raise ValueError(self.gettext('Not a valid choice'))

class Translations(object):
    messages={
        'Not a valid choice': u'不正な選択です',
        'Not a valid decimal value': u'数字または小数で入力してください',
        'Not a valid integer value': u'数字で入力してください',
        'Invalid email address.':u'不正なメールアドレスです',
        'This field is required.':u'入力してください',
        'Field must be at least %(min)d characters long.' : u'%(min)d文字以上で入力してください。',
        'Field cannot be longer than %(max)d characters.' : u'%(max)d文字以内で入力してください。',
        'Field must be between %(min)d and %(max)d characters long.' : u'%(min)d文字から%(max)d文字の間で入力してください。',
        'Not a valid datetime value': u'日時の形式を確認してください',
        'Not a valid date value': u'日付の形式を確認してください',
        'Invalid value for %(field)s': u'%(field)sに不正な値が入力されています',
        "Required field `%(field)s' is not supplied": u'「%(field)s」が空欄になっています',
        'year': u'年',
        'month': u'月',
        'day': u'日',
        'hour': u'時',
        'minute': u'分',
        'second': u'秒',
        }
    def __init__(self, messages = None):
        if messages:
            self.messages = dict(self.messages, **messages)

    def gettext(self, string):
        return self.messages.get(string, string)

    def ngettext(self, singular, plural, n):
        ural = singular if n == 1 else plural
        message  = self.messages.get(ural)
        if message:
            return message
        else:
            logger.warn("localize message not found: '%s'", ural)
            return ural


class Required(validators.Required):
    def __call__(self, form, field):
        # allow Zero input
        if field.data != 0:
            super(Required, self).__call__(form, field)

class RequiredOnUpdate(validators.Required):
    def __init__(self):
        self.delegated = Required()

    def __call__(self, form, field):
        if not getattr(form, 'new_form', False):
            self.delegated(form, field)

class Phone(validators.Regexp):
    def __init__(self, message=None):
        super(Phone, self).__init__(r'^[0-9¥-]*$', re.IGNORECASE, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext(u'電話番号を確認してください')
        super(Phone, self).__call__(form, field)

def text_type_but_none_if_not_given(value):
    return unicode(value) if value is not None else None

def Zenkaku(form, field):
    try:
        cp932_value = field.data.encode('Shift_JIS')
        if not re.match(r"^(?:[\x81-\x9f\xe0-\xfe][\x40-\x7e\x80-\xfc])+$", cp932_value):
            raise Exception()
    except:
        raise validators.ValidationError(field.gettext(u'全角で入力してください'))

Katakana = validators.Regexp(ur'^[ァ-ヶ]+$', message=u'カタカナで入力してください')

class JISX0208(object):
    def __init__(self, message=None):
        self.message = message or u'利用不可能な文字 (%(characters)s) が含まれています'

    def __call__(self, form, field):
        assert isinstance(field.data, unicode)
        bad_chars = set()
        for c in field.data:
            try:
                c.encode('Shift_JIS')
            except UnicodeEncodeError:
                bad_chars.add(c)
        if bad_chars:
            raise validators.ValidationError(field.gettext(self.message) % dict(characters=u'「' + u'」「'.join(bad_chars) + u'」'))


def NFKC(unistr):
    return unistr and unicodedata.normalize('NFKC', unistr)

def lstrip(chars):
    def stripper(unistr):
        return unistr and unistr.lstrip(chars)
    return stripper

def strip(chars):
    def stripper(unistr):
        return unistr and unistr.strip(chars)
    return stripper

REGEX_HYPHEN = re.compile('\-')
def strip_hyphen():
    def stripper(unistr):
        return unistr and REGEX_HYPHEN.sub('', unistr)
    return stripper

strip_spaces = strip(u' 　')

class SejCompliantEmail(validators.Regexp):
    def __init__(self, message=None):
        super(SejCompliantEmail, self).__init__(r'^[0-9A-Za-z_./+?-]+@(?:[0-9A-Za-z_-]+\.)*[0-9A-Za-z_-]+$', 0, message)

    def __call__(self, form, field):
        if self.message is None:
            self.message = field.gettext('Invalid email address.')
        if not field.data:
            return
        super(SejCompliantEmail, self).__call__(form, field)

def capitalize(unistr):
    return unistr and unistr.upper()

def ignore_regexp(regexp):
    def replace(target):
        if target is None:
            return None
        return re.sub(regexp, "", target)
    return replace

ignore_space_hyphen = ignore_regexp(re.compile(u"[ \-ー　]"))

class OurForm(Form):
    def __init__(self, *args, **kwargs):
        self.new_form = kwargs.pop('new_form', False)
        self._liaisons = fields and [name for name, unbound_field in self._unbound_fields if unbound_field.field_class == Liaison]
        super(OurForm, self).__init__(*args, **kwargs)

    def process(self, formdata=None, obj=None, **kwargs):
        if not self._liaisons:
            return super(OurForm, self).process(formdata, obj, **kwargs)

        if formdata is not None and not hasattr(formdata, 'getlist'):
            if hasattr(formdata, 'getall'): 
                formdata = WebobInputWrapper(formdata)
            else:
                raise TypeError("formdata should be a multidict-type wrapper that supports the 'getlist' method: ")

        for name, field in iteritems(self._fields):
            if obj is not None and hasattr(obj, name):
                field.process(formdata, getattr(obj, name))
            elif name in kwargs:
                field.process(formdata, kwargs[name])
            else:
                field.process(formdata)

        for name in self._liaisons:
            liaison = self._fields[name]
            counterpart = self._fields[liaison._counterpart]
            if not counterpart.data:
                counterpart.data = liaison.data
                liaison.data = None

def _gen_field_init(klass):
    def __init__(self, _form=None, hide_on_new=False, *args, **kwargs):
        super(klass, self).__init__(*args, **kwargs)
        self.form = _form
        self.hide_on_new=hide_on_new
    klass.__init__ = __init__

class OurTextField(fields.TextField):
    pass

_gen_field_init(OurTextField)

class OurSelectField(BugFreeSelectField):
    pass

_gen_field_init(OurSelectField)

class OurDecimalField(fields.DecimalField):
    pass

_gen_field_init(OurDecimalField)

class OurIntegerField(fields.IntegerField):
    pass

_gen_field_init(OurIntegerField)

class OurBooleanField(fields.BooleanField):
    pass
_gen_field_init(OurBooleanField)

Automatic = atom('Automatic')
Max = atom('Max')
Min = atom('Min')

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

class OurDateTimeFieldBase(fields.Field):
    _missing_value_defaults = dict(
        year=u'',
        month=u'1',
        day=u'1',
        hour=u'0',
        minute=u'0',
        second=u'0'
        )

    def _raise_undefined_minimum_error(field):
        def _(self, v):
            raise ValueError('minimum value for %s is not defined' % field)
        return _

    def _raise_undefined_maximum_error(field):
        def _(self, v):
            raise ValueError('maximum value for %s is not defined' % field)
        return _

    _min_max = {
        'year': {
            Min: _raise_undefined_minimum_error('year'),
            Max: _raise_undefined_maximum_error('year')
            },
        'month': {
            Min: lambda self, v: 1,
            Max: lambda self, v: 12
            },
        'day': {
            Min: lambda self, v: 1,
            Max: lambda self, v: days_of_month(year=v['year'], month=v['month'])
            },
        'hour': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 23
            },
        'minute': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            },
        'second': {
            Min: lambda self, v: 0,
            Max: lambda self, v: 59
            }
        }

    def __init__(self, _form=None, hide_on_new=False, label=None, validators=None, format='%Y-%m-%d %H:%M:%S', value_defaults=None, missing_value_defaults=None, allow_two_digit_year=True, **kwargs):
        super(OurDateTimeFieldBase, self).__init__(label, validators, **kwargs)
        self.form = _form
        self.hide_on_new = hide_on_new
        self.name_prefix = self.name + u'.'
        self.id_prefix = self.id + u'.'
        self.format = format
        self.value_defaults = value_defaults
        self.missing_value_defaults = missing_value_defaults or dict(self._missing_value_defaults)
        self.allow_two_digit_year = allow_two_digit_year
        self._values = dict((k, u'') for k in self._fields)

    def process_data(self, data):
        pass

    def process_datetime_formdata(self):
        values = dict()
        for k in self._fields:
            try:
                v = self._values[k] or self.missing_value_defaults[k]
                if isinstance(v, basestring):
                    if k == 'year' and self.allow_two_digit_year:
                        if len(v) == 2:
                            v = unicode(date.today().year // 100) + v
                    _v = int(v)
                else:
                    _v = self._min_max[k][v](self, values)
                values[k] = _v
            except ValueError:
                values[k] = None
                self.process_errors.append(self.gettext('Invalid value for %(field)s') % dict(field=self.gettext(k)))
        self.data = self._create_data(values)

    def process(self, formdata, data=_unset_value):
        self.process_errors = []
        if data is _unset_value:
            try:
                data = self.default()
            except TypeError:
                data = self.default

        self.object_data = data

        try:
            self.process_data(data)
        except ValueError as e:
            self.process_errors.append(e.args[0])

        if formdata:
            self.data = None
            if self.name in formdata:
                value = ' '.join(formdata.getlist(self.name))
                try:
                    self.process_data(datetime.strptime(value, self.format))
                except ValueError as e:
                    # XXX: for now we accept the following format '%Y-%m-%d %H:%M:%s' in addition for compatibility
                    warnings.warn(DeprecationWarning("OurDateTimeField's unwanted feature utilized"))
                    try:
                        self.process_data(datetime.strptime(value, '%Y-%m-%d %H:%M:%S'))
                    except ValueError as e:
                        self.process_errors.append(self.gettext('Not a valid datetime value'))
            else:
                missing_fields = []
                for k in self._fields:
                    v = u' '.join(formdata.getlist(self.name_prefix + k)).strip()
                    if not v:
                        missing_fields.append(k)
                        self._values[k] = u''
                    else:
                        self._values[k] = v
                        if missing_fields is not None:
                            for _k in missing_fields:
                                self.process_errors.append(self.gettext("Required field `%(field)s' is not supplied") % dict(field=self.gettext(_k)))
                            missing_fields = []
                if len(missing_fields) == len(self._fields):
                    self.data = None
                else:
                    self.process_datetime_formdata()
        else:
            try:
                value_defaults = self.value_defaults()
            except TypeError:
                value_defaults = self.value_defaults
            if value_defaults:
                for k in self._fields:
                    self._values[k] = value_defaults.get(k, u'')

        for filter in self.filters:
            try:
                self.data = filter(self.data)
            except ValueError as e:
                self.process_errors.append(e.args[0])


class OurDateTimeField(OurDateTimeFieldBase):
    widget = OurDateTimeWidget()
    _fields = ['year', 'month', 'day', 'hour', 'minute', 'second']

    def process_data(self, data):
        if data is None:
            for k in self._fields:
                self._values[k] = u''
        else:
            if not isinstance(data, datetime):
                raise TypeError()
            for k in self._fields:
                self._values[k] = getattr(data, k) 
        self.data = data

    def _create_data(self, values):
        try:
            return datetime(**values)
        except (TypeError, ValueError):
            self.process_errors.append(self.gettext('Not a valid datetime value'))

    def __call__(self, widget=None, **kwargs):
        if widget is None:
            widget = self.widget
        omit_second = self.format == '%Y-%m-%d %H:%M' # XXX
        return widget(self, omit_second=omit_second, **kwargs)

DateTimeField = OurDateTimeField # for compatibility

class OurDateField(OurDateTimeFieldBase):
    widget = OurDateWidget()
    _fields = ['year', 'month', 'day']

    def process_data(self, data):
        if data is None:
            for k in self._fields:
                self._values[k] = u''
        else:
            if isinstance(data, datetime):
                data = data.date()
            elif not isinstance(data, date):
                raise TypeError()
            for k in self._fields:
                self._values[k] = getattr(data, k) 
        self.data = data

    def _create_data(self, values):
        try:
            return date(**values)
        except (TypeError, ValueError):
            self.process_errors.append(self.gettext('Not a valid date value'))

    def __call__(self, widget=None, **kwargs):
        if widget is None:
            widget = self.widget
        return widget(self, **kwargs)

DateField = OurDateField

class NullableTextField(OurTextField):
    def process_formdata(self, valuelist):
        super(NullableTextField, self).process_formdata(valuelist)
        if self.data == '':
            self.data = None

class Liaison(fields.Field):
    @property
    def errors(self):
        return self._wrapped.errors

    @property
    def process_errors(self):
        return self._wrapped.process_errors

    @property
    def raw_data(self):
        return self._wrapped.raw_data

    @property
    def validators(self):
        return self._wrapped.validators

    @property
    def widget(self):
        return self._wrapped.widget

    @property
    def _translations(self):
        return self._wrapped._translations

    @property
    def do_not_call_in_templates(self):
        return self._wrapped.do_not_call_in_templates

    @property
    def data(self):
        return self._wrapped.data

    @property
    def form(self):
        return self._form

    @property
    def data(self):
        return self._data

    def gettext(self, string):
        return self._wrapped.gettext(string)

    def ngettext(self, singular, plural, n):
        return self._wrapped.ngettext(singular, plural, n)

    def validate(self, *args, **kwargs):
        return self._wrapped.validate(*args, **kwargs)

    def pre_validate(self, form):
        return self._wrapped.pre_validate(self, form)

    def post_validate(self, form, validation_stopped):
        return self._wrapped.post_validate(form, validation_stopped)

    def process(self, formdata=None, data=fields._unset_value):
        return self._wrapped.process(formdata, data)

    def validate(self, form, extra_validators=()):
        return self._wrapped.validate(form, extra_validators)

    def populate_obj(self, obj, name):
        return self._wrapped.populate_obj(obj, name)

    def append_entry(self, data=fields._unset_value):
        return self._wrapped.append_entry(data)

    def pop_entry(self):
        return self._wrapped.pop_entry()

    def __iter__(self):
        return self._wrapped.__iter__()

    def __len__(self):
        return self._wrapped.__len__()

    def __unicode__(self):
        return self._wrapped.__unicode__()

    def __str__(self):
        return self._wrapped.__str__()

    def __html__(self):
        return self._wrapped.__html__()

    def __call__(self, **kwargs):
        return self._wrapped(**kwargs)

    def __getitem__(self, index):
        return self._wrapped.__getitem__(index)

    def __getattr__(self, key):
        return getattr(self._wrapped, key)

    def __setattr__(self, key, value):
        if not key.startswith('_'):
            setattr(self._wrapped, key, value)
        else:
            object.__setattr__(self, key, value)

    def __init__(self, counterpart, wrapped, _form=None, _name=None, _prefix=None, _translations=None, **kwargs):
        if counterpart.__class__ == UnboundField:
            # resolve the field name from the unbound field object.
            for name, unbound_field in _form._unbound_fields:
                if unbound_field == counterpart:
                    counterpart = name
        self._counterpart = counterpart
        self._form = _form
        self._name = _name
        self._wrapped = wrapped.bind(_form, _name, _prefix, _translations, **kwargs)
