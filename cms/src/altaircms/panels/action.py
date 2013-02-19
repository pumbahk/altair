def model_action_buttons_panel(context, requst, obj, modelname, modeljname=None, _query=None):
    modeljname = modeljname or modelname
    D = _query.copy() if _query else {}
    D["id"] = obj.id
    return dict(obj=obj,
                modelname=modelname,
                modeljname=modeljname,
                _query=D)

def create_only_action_buttons_panel(context, request, modelname, modeljname=None, _query=None):
    modeljname = modeljname or modelname
    return dict(modelname=modelname,
                modeljname=modeljname,
                _query=_query or [])
