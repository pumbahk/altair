# -*- coding:utf-8 -*-
import wtforms
from wtforms import validators
from wtforms import fields
from wtforms import widgets


import logging
logger = logging.getLogger(__name__)
import wtforms.ext.sqlalchemy.fields as extfields
##
from wtforms.widgets.core import HTMLString
from wtforms.widgets.core import TextInput

class DatePickerInput(TextInput):
    """ a widget using bootstrap datepicker component
    """
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('type', self.input_type)
        if 'value' not in kwargs:
            kwargs['value'] = field._value()
            fmt = u"""
 <div class="date datepicker" data-date="">
  <input %s>
  <span class="add-on"><i class="icon-th"></i></span>
 </div>"""
            return HTMLString(fmt % self.html_params(name=field.name, **kwargs))
##
def datetime_pick_patch(): #slack-off
    """datetime field にclass="datepicker"をつける
    """ 
    target = fields.DateTimeField
    target.widget = DatePickerInput()


##
## query_select filter
##

class myQuerySelectField(extfields.QuerySelectField):
    """ wtformsのfieldではdataのNoneの場合、常にblankが初期値として設定されてしまっていた。
    　　それへの対応
    """
    def iter_choices(self):
        if self.allow_blank:
            yield (u'__None', self.blank_text, False)

        for pk, obj in self._get_object_list():
            status = self._get_selected_status(obj, self.data)
            yield (pk, self.get_label(obj), status)

    def _get_selected_status(self, obj, data):
        if data is None:
            return obj == data
        else:
            return obj.id == data.id or obj == data

from zope.interface import Interface
from zope.interface import provider

class IModelQueryFilter(Interface):
    def __call__(model, request, query):
        """ filter by this function in before view rendering
        """
        pass

@provider(IModelQueryFilter)
def model_query_filter_default(model, request, query):
    return request.allowable(model, qs=query)

def dynamic_query_select_field_factory(model, dynamic_query=None, name=None, **kwargs):
    """
    dynamic_query_factory: lambda model, request, query : ...

    * query_factoryが存在していない場合は提供
    """
    if not "query_factory" in kwargs:
        def _query_factory():
            field.query = model.query
            return field.query
        kwargs["query_factory"] = _query_factory

    field = myQuerySelectField(**kwargs)

    name = name or model.__name__
    def dynamic_query_filter(field, form=None, rendering_val=None, request=None):
        field._object_list = None
        #hack . this is almost wrong.(if calling memoize function field.get_object_list() using this field as cache store))

        if getattr(field, "query", None):
            query = field.query
        else:
            query = field.query_factory()

        if dynamic_query:
            query_filter = dynamic_query
        else:
            query_filter = request.registry.queryUtility(IModelQueryFilter,
                                                         name, 
                                                     model_query_filter_default)
        field.query = query_filter(model, request, query)
    field._dynamic_query = dynamic_query_filter
    return field


class MaybeDateTimeField(fields.DateTimeField):
    def process_formdata(self, valuelist):
        if not valuelist:
            self.data = None
        elif valuelist[0] == u"":
            self.data = None
        else:
            super(MaybeDateTimeField, self).process_formdata(valuelist)

def required_field(message=None):
    if message is None:
        message = u"このフィールドは必須です。"
    return Required(message=message)

def append_errors(errors, key, v):
    if key not in errors:
        errors[key] = []
    errors[key].append(v)
    return errors

class Required(object):
    field_flags = ('required', )

    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data or isinstance(field.data, basestring) and not field.data.strip():
            if self.message is None:
                self.message = field.gettext(u'This field is required.')
            raise validators.StopValidation(self.message)

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
        'Not a valid datetime value': u'日付の形式を確認してください',
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

class Form(wtforms.Form):
    def _get_translations(self):
        return Translations()
    
