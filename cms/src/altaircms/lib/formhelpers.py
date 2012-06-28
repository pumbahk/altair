# -*- coding:utf-8 -*-
import wtforms.fields as fields
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
from zope.interface import Attribute
from zope.interface import implementer

class IModelQueryFilter(Interface):
    model = Attribute("target model")

    def __call__(query):
        pass

@implementer(IModelQueryFilter)
class ModelQueryFilterDefault(object):
    def __init__(self, model):
        self.model = model

    def __call__(self, request, query):
        if getattr(request, "site"):
            return query.filter_by(site_id=request.site.id)
        else:
            return query

def dynamic_query_select_field_factory(model, dynamic_query_factory=None, factory_name=None, **kwargs):
    """
    dynamic_query_factory: lambda field, form=None, rendering_val=None, request=None : ...

    * query_factoryが存在していない場合はてきとーに提供
    * dynamic_query_factoryをさらに追加
    """
    if not "query_factory" in kwargs:
        def _query_factory():
            field.query = model.query
            return field.query
        kwargs["query_factory"] = _query_factory
    factory_name = factory_name or model.__name__.lower()

    field = myQuerySelectField(**kwargs)
    def dynamic_query(field_data, form, rendering_val, request):
        query_filter = request.registry.queryUtility(IModelQueryFilter,
                                                     model.__name__, 
                                                     ModelQueryFilterDefault)
        query = field.query_factory()
        field_data.choices = query_filter(query, request)
    field._dynamic_query = dynamic_query
    return field

