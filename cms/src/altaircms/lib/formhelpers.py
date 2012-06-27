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

class IModelQueryFilterAdaptor(Interface):
    model = Attribute("target model")

def add_dynamic_query_select
def dynamic_query_select_field_factory(model, dynamic_query_factory=None, factory_name=None, **kwargs):
    """
    dynamic_query_factory: lambda field, form=None, rendering_val=None, request=None : ...

    * query_factoryが存在していない場合はてきとーに提供
    * dynamic_query_factoryをさらに追加
        * dynamic_query_factoryが無いときはデフォルトの関数を呼び出す。
           * factory_nameがあるとき -> DynamicQueryDefaultからその名前のメソッドを探す
           * factory_nameが無いとき -> model.__name__.lower()のメソッドを探す
    """
    if not "query_factory" in kwargs:
        def _query_factory():
            field.query = model.query
            return field.query
        kwargs["query_factory"] = _query_factory
    factory_name = factory_name or model.__name__.lower()

    field = myQuerySelectField(**kwargs)
    field._dynamic_query = DynamicQueryChoicesDispatcher.dispatch(
        factory_name, 
        dynamic_query_factory)
    return field

