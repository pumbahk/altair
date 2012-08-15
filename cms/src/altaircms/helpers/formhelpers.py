# -*- coding:utf-8 -*-
from wtforms import validators
from wtforms import fields
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
