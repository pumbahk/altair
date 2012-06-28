# -*- encoding:utf-8 -*-

##enxtend version at crud.UpdateView.input
from altaircms.models import Performance
from . import forms
from . import mappers

## ``init``.pyで登録している
def performance_detail(request):
    obj = Performance.query.filter_by(id=request.matchdict["id"]).first()
    form = forms.PerformanceForm()
    return {"performance": obj, 
            "event": obj.event, 
            "form": form, 
            "mapped": mappers.performance_mapper(request, obj), 
            "display_fields": form.__display_fields__}

