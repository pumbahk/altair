# -*- coding:utf-8 -*-
import wtforms.fields as fields
import wtforms.ext.sqlalchemy.fields as extfields

def datetime_pick_patch(): #slack-off
    """datetime field にclass="datepicker"をつける
    """ 
    _kwargs_defaults = {"class_": "datepicker"}

    from functools import wraps
    def with_args(method):
        @wraps(method)
        def wrapped(self, **kwargs):
            if not "class_" in kwargs:
                kwargs.update(_kwargs_defaults)
            return method(self, **kwargs)
        return wrapped
    target = fields.DateTimeField
    target.__call__ = with_args(target.__call__)


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
    def image_asset(cls, info, qs, field):
        field.query = cls._filter_by_site(qs, info.request)
    @classmethod
    def widgetdisposition(cls, info, qs, field):
        qs = cls._filter_by_site(info, info.qs, info.request)
        from altaircms.widget.models import WidgetDisposition
        field.query = WidgetDisposition.enable_only_query(info.request.user, qs=qs)
        
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

    field = extfields.QuerySelectField(**kwargs)
    field._dynamic_query = DynamicQueryChoicesDispatcher.dispatch(
        factory_name, 
        dynamic_query_factory)
    return field
