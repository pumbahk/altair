def login_url(request):
    membership = request.context.membership
    return request.route_url('fc_auth.login', membership=membership)

