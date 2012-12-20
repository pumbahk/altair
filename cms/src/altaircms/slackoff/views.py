# -*- encoding:utf-8 -*-

##enxtend version at crud.UpdateView.input
import altaircms.helpers as h
from . import forms
from . import mappers
from ..models import Category, Performance

## ``init``.pyで登録している
def performance_detail(request):
    obj = Performance.query.filter_by(id=request.matchdict["id"]).first()
    form = forms.PerformanceForm()
    return {"performance": obj, 
            "event": obj.event, 
            "form": form, 
            "mapped": mappers.performance_mapper(request, obj), 
            "display_fields": form.__display_fields__}

def category_list_view(context, request):
    qs = request.allowable(Category)
    form = forms.CategoryForm()
    return {"categories": h.paginate(request, qs, item_count=qs.count()), 
            "form": form, 
            "mapper": mappers.category_mapper, 
            "display_fields": form.__display_fields__}
