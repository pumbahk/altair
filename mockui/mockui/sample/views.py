from pyramid.view import view_config
from pyramid.response import Response
from tmpstorage import get_storage
from stage import get_stage
from mockui.fanstatic import jqueries_need
import json

@view_config(route_name="sample::sample", renderer="sample/sample.mak")
def sample_view(request):
    jqueries_need()
    return {}

### api
@view_config(route_name="sample::api_load_stage", renderer="json")
def load_stage_view(request):
    try:
        storage = get_storage()
        info = get_stage(storage)
        return dict(status="success", stage=info.stage, 
                    layoutname=info.layoutname, context=info.context)
    except Exception, e:
        return dict(status="fail", message=str(e))

@view_config(route_name="sample::api_load_layout", renderer="sample/selected_layout.mak")
def load_layout_view(request):
    """
    :params:
    prefix: <string>
    """
    layout = request.GET.get("layout") or get_storage().layout
    prefix = request.GET["prefix"]
    return dict(prefix=prefix, layout=layout)


@view_config(route_name="sample::api_save_layout", renderer="json")
def save_layout_view(request):
    """
    :params:
    layout_name: <string>
    """
    storage = get_storage()
    storage.save_layout(request.POST["layout_name"])
    return dict(status="success", result=storage.layout)

@view_config(route_name="sample::api_load_block", renderer="json")
def load_block_view(request):
    pass

@view_config(route_name="sample::api_move_block", renderer="json")
def move_block_view(request):
    """
    :params: 
    old_block: <string>
    block_name: <string>
    orderno: <int>
    """
    storage = get_storage()
    old_block = request.POST["old_block"]
    old_orderno = request.POST["old_orderno"]
    block_name = request.POST["block_name"]
    orderno = request.POST["orderno"]
    storage.move_block(old_block, old_orderno, block_name, orderno)
    return Response("ok")


@view_config(route_name="sample::api_save_block", renderer="json")
def save_block_view(request):
    """
    :params: 
    block_name: <string>
    widget_name: <string>
    orderno: <int>
    """
    storage = get_storage()
    block_name = request.POST["block_name"]
    orderno = request.POST["orderno"]
    widget_name = request.POST["widget_name"]
    storage.save_block(block_name, orderno, widget_name)
    return Response("ok")


@view_config(route_name="sample::api_load_widget", renderer="json")
def load_widget_view(request):
    """
    :params:
    block_name: <string>
    orderno: <int>
    """
    storage = get_storage()
    block_name = request.GET["block_name"]
    orderno = request.GET["orderno"]
    val = storage.load_block(block_name, orderno)
    widget_name = val["widget_name"]
    from pyramid.view import render_view_to_response
    ## widget name : a name of widget.py's view.
    return render_view_to_response(None, request, name=widget_name)



@view_config(route_name="sample::api_delete_widget", renderer="json")
def delete_widget_view(request):
    """
    :params:
    block_name: <string>
    orderno: <int>
    """
    storage = get_storage()
    block_name = request.POST["block_name"]
    orderno = request.POST["orderno"]
    status = storage.delete_widget(block_name, orderno)
    return dict(status="success")

@view_config(route_name="sample::api_save_widget", renderer="json")
def save_widget_view(request):
    """
    :params:
    widget_name: <string>
    block_name: <string>
    orderno: <int>
    data: <json>
    """
    storage = get_storage()
    widget_name = request.POST["widget_name"]
    block_name = request.POST["block_name"]
    orderno = request.POST["orderno"]
    data = json.loads(request.POST["data"])

    storage.save_widget(widget_name, block_name, orderno, data)
    return dict(status="success")


