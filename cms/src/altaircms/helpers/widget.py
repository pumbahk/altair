def to_disposition_list(request):
    return request.route_path("disposition_list")

def to_disposition_alter(request, d):
    return request.route_path("disposition_alter", id=d.id)
