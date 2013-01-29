# -*- coding:utf-8 -*-

import re
from datetime import datetime
from exceptions import ValueError
import unicodedata

from wtforms import validators, fields
from wtforms.form import Form, WebobInputWrapper
from wtforms.fields.core import UnboundField
from wtforms.compat import iteritems
import logging

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

class OurDateTimeField(fields.DateTimeField):
    '''
    Customized field definition datetime format of "%Y-%m-%d %H:%M"
    '''

    def _value(self):
        if self.raw_data:
            try:
                dt = datetime.strptime(self.raw_data[0], '%Y-%m-%d %H:%M:%S')
                return dt.strftime(self.format)
            except:
                return u' '.join(self.raw_data)
        else:
            return self.data.strftime(self.format) if self.data else u''

    def process_formdata(self, valuelist):
        if valuelist:
            date_str = u' '.join(valuelist)
            if date_str:
                try:
                    self.data = datetime.strptime(date_str, self.format)
                except ValueError:
                    self.data = None
                    raise validators.ValidationError(u'日付の形式を確認してください')

_gen_field_init(OurDateTimeField)

DateTimeField = OurDateTimeField # for compatibility

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
