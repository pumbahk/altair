def entry_index(request):
    return request.route_url('lots.entry.index', **request.matchdict)


def entry_confirm(request):
    return request.route_url('lots.entry.confirm', **request.matchdict)


def entry_completion(request):
    return request.route_url('lots.entry.completion', **request.matchdict)


def payment_completion(request):
    return request.route_url('lots.payment.completion', **request.matchdict)
           
