import os
import time
import hmac
import struct
import base64
from hashlib import sha1
from wtforms import form, fields
from wtforms.ext.csrf import SecureForm
from wtforms.ext.csrf.fields import CSRFTokenField
from wtforms.fields.core import UnboundField
from wtforms.compat import iteritems
from wtforms.validators import ValidationError
from .fields.liaison import Liaison
from .utils.mixin import override, make_class_factory

__all__ = [
    'OurForm',
    'OurDynamicForm',
    'SecureFormMixin',
    ]

form_class_factory = make_class_factory(form.Form.__class__)

class OurForm(form.Form):
    __metaclass__ = form_class_factory

    def __init__(self, formdata=None, obj=None, prefix='', **kwargs):
        self.new_form = kwargs.pop('new_form', False)
        self._name_builder = kwargs.pop('name_builder', None)
        self._liaisons = fields and [name for name, unbound_field in self._unbound_fields if unbound_field.field_class == Liaison]
        super(OurForm, self).__init__(formdata, obj, prefix, **kwargs)

    def __setitem__(self, overridden, name, value):
        self._fields[name] = value.bind(form=self, name=name, prefix=self._prefix, name_builder=self._name_builder)

    def __contains__(self, k):
        return k in self._fields

    def process(self, formdata=None, obj=None, _data=None, **kwargs):
        if formdata is not None and not hasattr(formdata, 'getlist'):
            if hasattr(formdata, 'getall'): 
                formdata = form.WebobInputWrapper(formdata)
            else:
                raise TypeError("formdata should be a multidict-type wrapper that supports the 'getlist' method: ")

        for name, field in iteritems(self._fields):
            if name in kwargs:
                field.process(formdata, kwargs[name])
            elif _data is not None and field.short_name in _data:
                field.process(formdata, _data[field.short_name])
            elif obj is not None:
                if hasattr(field, 'process_obj'):
                    field.process_obj(formdata, name)
                elif hasattr(obj, name):
                    if hasattr(field, 'fetch_value_from_obj'):
                        value = field.fetch_value_from_obj(obj, name)
                    else:
                        value = getattr(obj, name)
                    field.process(formdata, value)
                else:
                    field.process(formdata)
            else:
                field.process(formdata)

        if self._liaisons:
            for name in self._liaisons:
                liaison = self._fields[name]
                counterpart = self._fields[liaison._counterpart]
                if not counterpart.data:
                    counterpart.data = liaison.data
                    liaison.data = None

    def clear_errors(self):
        for name, f in iteritems(self._fields):
            f.errors = ()
        self._errors = None


class OurDynamicForm(OurForm):
    def __init__(self, formdata=None, obj=None, prefix='', *args, **kwargs):
        dynamic_fields = kwargs.pop('_fields', [])
        _data = kwargs.pop('_data', None)
        self._translations = kwargs.pop('_translations', None)
        self._initializing = dynamic_fields
        super(OurDynamicForm, self).__init__(formdata, obj, prefix, *args, **kwargs)
        self._initializing = None
        self.process(formdata=formdata, obj=obj, _data=_data, **kwargs)

    def _get_translations(self):
        if callable(self._translations):
            return self._translations()
        else:
            return self._translations

    def process(self, formdata=None, obj=None, _data=None, **kwargs):
        if self._initializing is not None:
            translations = self._get_translations()
            unbound_fields = list(self._unbound_fields)
            for name, unbound_field in self._initializing:
                field = unbound_field.bind(form=self, name=name, prefix=self._prefix, translations=translations, name_builder=self._name_builder)
                self._fields[name] = field
                unbound_fields.append((name, unbound_field))
            self._unbound_fields = unbound_fields
        else:
            return super(OurDynamicForm, self).process(formdata=formdata, obj=obj, _data=_data, **kwargs)

    def validate(self):
        extra = {}
        for name in self._fields:
            method_name = u'validate_%s' % name
            try:
                inline = getattr(self.__class__, method_name, None)
            except UnicodeEncodeError:
                # Should never happen in Py3k
                inline = None
            if inline is not None:
                extra[name] = [inline]
        return super(form.Form, self).validate(extra)

class SecureFormMixin(object):
    TIME_LIMIT = 1800
    SESSION_KEY = 'csrf'
    SECRET_KEY = ''

    def __mixin_init_pre__(self, **kwargs):
        self._csrf_context = kwargs.pop('csrf_context')
        self._current_token = self._get_csrf_key() or u''
        return kwargs

    def __mixin_init_post__(self, **kwargs):
        csrf_token_field = None
        for field in self._fields.values():
            if isinstance(field, CSRFTokenField):
                csrf_token_field = field
        if csrf_token_field is not None:
            csrf_token_field.current_token = self.generate_csrf_token()
        self._csrf_token_field = csrf_token_field

    def _get_csrf_key(self):
        session = getattr(self._csrf_context, 'session', self._csrf_context)
        csrf_key = session[self.SESSION_KEY] if self.SESSION_KEY in session else None
        return csrf_key

    def _set_csrf_key(self, csrf_key):
        session = getattr(self._csrf_context, 'session', self._csrf_context)
        session[self.SESSION_KEY] = csrf_key

    def generate_csrf_token(self):
        csrf_key = sha1(os.urandom(64)).hexdigest()
        self._set_csrf_key(csrf_key)
        csrf_build = csrf_key
        if self.TIME_LIMIT:
            expires = self._encode_time_for_csrf_token(time.time() + self.TIME_LIMIT)
            csrf_build += expires
        else:
            expires = ''
        hmac_csrf = hmac.new(self.SECRET_KEY, csrf_build.encode('utf-8'), digestmod=sha1)
        return u'%s##%s' % (expires, hmac_csrf.hexdigest())

    @property
    def data(self):
        d = super(SecureFormMixin, self).data
        if self._csrf_token_field is not None:
            d.pop(self._csrf_token_field.name)
        return d

    def _encode_time_for_csrf_token(self, v):
        return base64.b16encode(struct.pack('>Q', v))

    def _decode_time_for_csrf_token(self, tv):
        return struct.unpack('>Q', base64.b16decode(tv))

    def _validate_csrf_token(self):
        if self._csrf_token_field is None:
            return True
        f = self._csrf_token_field
        v = f.data
        f.errors = list(f.process_errors)
        if not v or u'##' not in v:
            f.errors.append(f.gettext(u'CSRF token missing'))
            return False
        expires, hmac_csrf = v.split(u'##')
        check_val = (self._current_token + expires).encode('utf-8')
        hmac_compare = hmac.new(self.SECRET_KEY, check_val, digestmod=sha1)
        if hmac_compare.hexdigest() != hmac_csrf:
            f.errors.append(f.gettext(u'CSRF failed'))
            return False

        if self.TIME_LIMIT:
            t = self._decode_time_for_csrf_token(expires)    
            if time.time() > t:
                f.errors.append(f.gettext('CSRF token expired'))
                return False
        return True

    @override
    def validate(self, _validate):
        return all([self._validate_csrf_token(), _validate(self)])

