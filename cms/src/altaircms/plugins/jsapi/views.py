from altaircms.models import DBSession
from altaircms.models import Performance

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
