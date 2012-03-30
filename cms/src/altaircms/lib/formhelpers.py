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

class DynamicQueryChoicesDefault(object):
    """ formのselect_query_fieldの絞り込みの方法を提供するクラス
        todo: logging
    """
    def __init__(self, form=None, rendering_val=None, request=None):
        self.form = form
        self.rendering_val = rendering_val
        self.request = request

    @classmethod
    def dispatch(cls, model):
        method_name = model.__name__.lower()
        def _query_refinement(field, form=None, rendering_val=None, request=None):
            instance = cls(form=form, rendering_val=rendering_val, request=request)
            return getattr(instance, method_name)(field)
        return _query_refinement

    def _filter_by_site(self, qs, request):
        if hasattr(self.request, "site"):
            qs = qs.filter_by(site_id=self.request.site.id)
        return qs

    ###
    def layout(self, field):
        field.query = self._filter_by_site(field.query, self.request)

    
        
def dynamic_query_select_field_factory(model, dynamic_query_factory=None, **kwargs):
    """
    dynamic_query_factory: lambda field, form=None, rendering_val=None, request=None : ...
    """
    if not "query_factory" in kwargs:
        def _query_factory():
            field.query = model.query
            return field.query
        kwargs["query_factory"] = _query_factory

    field = extfields.QuerySelectField(**kwargs)
    if dynamic_query_factory:
        field._dynamic_query = dynamic_query_factory
    else:
        field._dynamic_query = DynamicQueryChoicesDefault.dispatch(model)
    return field
