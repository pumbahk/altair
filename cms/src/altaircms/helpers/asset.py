def to_show_page(request, asset):
    return request.route_url("asset_edit", asset_id=asset.id, _query=dict(raw="t"))
