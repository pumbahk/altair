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

from altaircms.models import DBSession
def performance_add_getti_code(request):
    ## todo: refactoring
    params = request.params
    codes = {}
    changed = []
    for k, getti_code in params.items():
        _, i = k.split(":", 1)
        codes[int(i)] = getti_code

    for obj in Performance.query.filter(Performance.id.in_(codes.keys())):
        changed.append(obj.id)
        getti_code = codes[obj.id]

        pc = "https://www.e-get.jp/tstar/pt/&s=%s" % getti_code
        mb = "https://www.e-get.jp/tstar/mt/&s=%s" % getti_code
        obj.purchase_link = pc
        obj.mobile_purchase_link = mb
        DBSession.add(obj)

    return {"status": "ok", 
            "changed": changed}
