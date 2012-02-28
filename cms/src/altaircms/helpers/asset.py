def to_show_page(request, asset):
    if hasattr(asset, "image_path"): # for movie, flash
        query = dict(filepath="image_path")
    else:
        query = dict()
    return request.route_url("asset_display", asset_id=asset.id, _query=query)
