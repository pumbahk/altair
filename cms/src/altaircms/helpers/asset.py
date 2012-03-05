def to_show_page(request, asset, filepath=None):
    if filepath is None:
        query = dict()
    elif filepath and hasattr(asset, filepath): # for movie, flash
        query = dict(filepath=filepath)
    else:
        raise Exception("invalid filepath %s" % filepath)
    return request.route_url("asset_display", asset_id=asset.id, _query=query)
