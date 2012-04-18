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

class DynamicQueryChoicesDispatcher(object):
    """ formのselect_query_fieldの絞り込みの方法を提供するクラス
        todo: logging
    """
    def __init__(self, form=None, rendering_val=None, request=None):
        self.form = form
        self.rendering_val = rendering_val
        self.request = request

    @classmethod
    def dispatch(cls, method_name, mfn_default):
        def _query_refinement(field, form=None, rendering_val=None, request=None):
            mfn = mfn_default
            instance = cls(form=form, rendering_val=rendering_val, request=request)
            if mfn is None:
                mfn = getattr(DynamicQueryDefault, method_name)
            return mfn(instance, instance._get_qs(field), field)
        return _query_refinement

    def _get_qs(self, field):
        if field.query:
            return field.query

        if field.query_factory:
            field.query = field.query_factory()
            return field.query
        raise Exception("foo")

class DynamicQueryDefault(object):
    @classmethod
    def _filter_by_site(cls, qs, request):
        if hasattr(request, "site"):
            qs = qs.filter_by(site_id=request.site.id)
        return qs

    @classmethod
    def layout(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def page(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def event(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def imageasset(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def pageset(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def operator(cls, info, qs, field):
        field.query = qs
    @classmethod
    def widgetdisposition(cls, info, qs, field):
        qs = cls._filter_by_site(info, info.qs, info.request)
        from altaircms.widget.models import WidgetDisposition
        field.query = WidgetDisposition.enable_only_query(info.request.user, qs=qs)


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
