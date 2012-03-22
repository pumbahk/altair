def to_save_disposition(request, page):
    return request.route_path("disposition_save", id=page.id)

def to_load_disposition(request, page):
    return request.route_path("disposition_save", id=page.id)
