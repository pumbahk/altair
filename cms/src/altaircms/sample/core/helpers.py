def to_edit_page(request, page_id):
    return request.route_url("sample::edit_page", page_id=page_id)
