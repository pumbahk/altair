def model_action_buttons_panel(context, requst, obj, modelname, _query=None):
    return dict(obj=obj, modelname=modelname, _query=_query or [])
